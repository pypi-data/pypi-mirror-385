from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, TypeVar, Union

import dask.dataframe as dd
import pandas as pd
from fsspec import AbstractFileSystem
from pydantic import BaseModel

from sibi_dst.df_helper.core import QueryConfig, ParamsConfig
from sibi_dst.utils import ManagedResource, ParquetSaver, ClickHouseWriter
from .backends.http import HttpConfig
from .backends.parquet import ParquetConfig
from .backends.sqlalchemy import SqlAlchemyConnectionConfig, SqlAlchemyLoadFromDb

T = TypeVar("T", bound=BaseModel)

def _is_dask_df(x) -> bool:
    return isinstance(x, dd.DataFrame)

def _maybe_persist(df, persist: bool):
    return df.persist() if persist and _is_dask_df(df) else df

def _maybe_compute(df, as_pandas: bool):
    return df.compute() if as_pandas and _is_dask_df(df) else df


# ---- Backend Strategy Pattern ----
class BaseBackend:
    def __init__(self, helper: "DfHelper"):
        self.helper = helper
        self.logger = helper.logger
        self.debug = helper.debug
        self.total_records = -1

    def load(self, **options) -> Union[tuple[Any, Any], dd.DataFrame, pd.DataFrame]:
        raise NotImplementedError

    async def aload(self, **options) -> Union[tuple[Any, Any], dd.DataFrame, pd.DataFrame]:
        return await asyncio.to_thread(self.load,**options)


class SqlAlchemyBackend(BaseBackend):
    def load(self, **options):
        try:
            if options and hasattr(self.helper._backend_params, "parse_params"):
                self.helper._backend_params.parse_params(options)

            with SqlAlchemyLoadFromDb(
                plugin_sqlalchemy=self.helper.backend_db_connection,
                plugin_query=self.helper._backend_query,
                plugin_params=self.helper._backend_params,
                logger=self.logger,
                debug=self.debug,
            ) as db_loader:
                self.total_records, result = db_loader.build_and_load()
                return self.total_records, result
        except Exception as e:
            self.logger.error(f"Failed to load data from sqlalchemy: {e}", exc_info=self.debug, extra=self.helper.logger_extra)
            return -1, dd.from_pandas(pd.DataFrame(), npartitions=1)


class ParquetBackend(BaseBackend):
    def load(self, **options):
        try:
            df = self.helper.backend_parquet.load_files(**options)
            if not self.helper._has_any_rows(df):
                self.total_records = 0
                return 0, self._empty_like(df)

                # Let DfHelper decide about persist
            self.total_records = -1  # unknown without full count
            return self.total_records, df

        except Exception as e:
            self.total_records = -1  # Reset total_records on failure
            self.logger.error(f"Failed to load data from parquet: {e}", exc_info=self.debug, extra=self.helper.logger_extra)
            return -1, dd.from_pandas(pd.DataFrame(), npartitions=1)

    @staticmethod
    def _empty_like(ddf):
        empty_pdf = ddf._meta.iloc[0:0]
        return dd.from_pandas(empty_pdf, npartitions=1)


class HttpBackend(BaseBackend):
    def load(self, **options):
        # Avoid event-loop problems in sync code paths.
        # If someone calls .load() on an async backend, make it explicit.
        raise RuntimeError(
            "HttpBackend.load() is sync but this backend is async-only. "
            "Call `await helper.aload(...)` or `await helper.load_async(prefer_native=True, ...)`."
        )

    async def aload(self, **options):
        if not self.helper.backend_http:
            self.logger.warning("HTTP plugin not configured properly.", extra=self.helper.logger_extra)
            self.total_records = -1
            return self.total_records, dd.from_pandas(pd.DataFrame(), npartitions=1)

        result = await self.helper.backend_http.fetch_data(**options)

        # Normalize to DataFrame if the plugin returns list/dict
        if isinstance(result, (list, dict)):
            pdf = pd.DataFrame(result)
            ddf = dd.from_pandas(pdf, npartitions=max(1, min(32, len(pdf) // 50_000 or 1)))
            self.total_records = len(pdf)
            return self.total_records, ddf

        if isinstance(result, pd.DataFrame):
            self.total_records = len(result)
            ddf = dd.from_pandas(result, npartitions=max(1, min(32, len(result) // 50_000 or 1)))
            return self.total_records, ddf

        # Fallback
        self.total_records = -1
        return self.total_records, dd.from_pandas(pd.DataFrame(), npartitions=1)


class DfHelper(ManagedResource):
    _BACKEND_STRATEGIES = {
        "sqlalchemy": SqlAlchemyBackend,
        "parquet": ParquetBackend,
        "http": HttpBackend,
    }

    _BACKEND_ATTR_MAP = {
        "sqlalchemy": "backend_db_connection",
        "parquet": "backend_parquet",
        "http": "backend_http",
    }

    default_config: Dict[str, Any] = None
    logger_extra: Dict[str, Any] = {"sibi_dst_component": __name__}

    def __init__(self, backend="sqlalchemy", **kwargs):
        self.default_config = self.default_config or {}
        kwargs = {**self.default_config.copy(), **kwargs}
        kwargs.setdefault("auto_sse", False)
        super().__init__(**kwargs)
        self.backend = backend

        # Ensure defaults flow to plugin configs
        kwargs.setdefault("debug", self.debug)
        kwargs.setdefault("fs", self.fs)
        kwargs.setdefault("logger", self.logger)

        self.total_records = -1
        self._backend_query = self._get_config(QueryConfig, kwargs)
        self._backend_params = self._get_config(ParamsConfig, kwargs)

        self.backend_db_connection: Optional[SqlAlchemyConnectionConfig] = None
        self.backend_parquet: Optional[ParquetConfig] = None
        self.backend_http: Optional[HttpConfig] = None

        if self.backend == "sqlalchemy":
            self.backend_db_connection = self._get_config(SqlAlchemyConnectionConfig, kwargs)
        elif self.backend == "parquet":
            self.backend_parquet = self._get_config(ParquetConfig, kwargs)
        elif self.backend == "http":
            self.backend_http = self._get_config(HttpConfig, kwargs)

        strategy_cls = self._BACKEND_STRATEGIES.get(self.backend)
        if not strategy_cls:
            raise ValueError(f"Unsupported backend: {self.backend}")
        self.backend_strategy = strategy_cls(self)

    # ---------- ManagedResource hooks ----------
    def get_sse(self):
        return self._ensure_sse()

    def _emit_bg(self, event: str, **data: Any) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # no running loop: run to completion
            asyncio.run(self.emit(event, **data))
        else:
            loop.create_task(self.emit(event, **data))

    def _cleanup(self):
        attr_name = self._BACKEND_ATTR_MAP.get(self.backend)
        if not attr_name:
            self.logger.warning(f"No attribute mapping found for backend '{self.backend}'. Cleanup skipped.", extra=self.logger_extra)
            return
        active_config = getattr(self, attr_name, None)
        if active_config and hasattr(active_config, "close"):
            self.logger.debug(f"{self.__class__.__name__} is closing resources for backend '{self.backend}' backend using attribute '{attr_name}'.", extra=self.logger_extra)
            active_config.close()

    async def _acleanup(self):
        self.logger.warning(
            "DfHelper instance was not used in an async context manager; cleanup is being called manually.",
            extra=self.logger_extra,
        )
        attr_name = self._BACKEND_ATTR_MAP.get(self.backend)
        if not attr_name:
            self.logger.warning(f"No attribute mapping found for backend '{self.backend}'. Cleanup skipped.", extra=self.logger_extra)
            return
        active_config = getattr(self, attr_name, None)
        if active_config and hasattr(active_config, "aclose"):
            self.logger.debug(f"Closing resources for '{self.backend}' backend using attribute '{attr_name}'.", extra=self.logger_extra)
            await active_config.aclose()

    # ---------- config helpers ----------
    def _get_config(self, model: T, kwargs: Dict[str, Any]) -> T:
        recognized = set(model.model_fields.keys())
        model_kwargs = {k: kwargs[k] for k in recognized if k in kwargs}
        return model(**model_kwargs)

    # ---------- load/aload ----------
    def load(self, *, persist: bool = False, as_pandas: bool = False, **options) -> Union[pd.DataFrame, dd.DataFrame]:
        self.logger.debug(f"Loading data from {self.backend} backend with options: {options}", extra=self.logger_extra)
        self.total_records, df = self.backend_strategy.load(**options)
        df = self._process_loaded_data(df)
        df = self._post_process_df(df)
        df = _maybe_persist(df, persist)
        return _maybe_compute(df, as_pandas)

    async def aload(
        self,
        *,
        persist: bool = False,
        as_pandas: bool = False,
        timeout: Optional[float] = None,
        **options
    ) -> Union[pd.DataFrame, dd.DataFrame]:
        await self.emit(f"{self.__class__.__name__} load:start", message=f"Pulling data from {self.backend} backend")
        # 1) Async load if available, else run sync load in a thread.
        if hasattr(self.backend_strategy, "aload"):
            load_awaitable = self.backend_strategy.aload(**options)
        else:
            # Run ONLY the backend load step in a thread to avoid event-loop blocking.
            load_awaitable = asyncio.to_thread(self.backend_strategy.load, **options)

        total, df = await (asyncio.wait_for(load_awaitable, timeout) if timeout else load_awaitable)
        self.total_records = total

        # 2) Post-processing steps are sync; offload to threads.
        await self.emit(event=f"{self.__class__.__name__} load:progress", message=f"Post-processing {len(df)} records")
        df = await asyncio.to_thread(self._process_loaded_data, df)
        df = await asyncio.to_thread(self._post_process_df, df)

        # 3) Persist and compute can block; offload when needed.
        if persist and _is_dask_df(df):
            df = await asyncio.to_thread(df.persist)
        if as_pandas and _is_dask_df(df):
            # Allow separate timeout for compute if desired; reuse same timeout here.
            compute_awaitable = asyncio.to_thread(df.compute)
            return await (asyncio.wait_for(compute_awaitable, timeout) if timeout else compute_awaitable)

        await self.emit(event=f"{self.__class__.__name__} load:progress", message=f"Returning {len(df)} records")

        return df

    # ---------- dataframe post-processing ----------
    def _post_process_df(self, df: dd.DataFrame) -> dd.DataFrame:
        self.logger.debug(f"{self.__class__.__name__} is post-processing resulting dataframe with {len(df)} records.", extra=self.logger_extra)
        df_params = self._backend_params.df_params
        if not df_params:
            return df
        fieldnames = df_params.get("fieldnames")
        column_names = df_params.get("column_names")
        index_col = df_params.get("index_col")

        if fieldnames:
            valid = [f for f in fieldnames if f in df.columns]
            if len(valid) < len(fieldnames):
                self.logger.warning(f"Missing columns for filtering: {set(fieldnames) - set(valid)}", extra=self.logger_extra)
            df = df[valid]
        if column_names:
            if len(df.columns) != len(column_names):
                raise ValueError(
                    f"Length mismatch: DataFrame has {len(df.columns)} columns, but {len(column_names)} names were provided."
                )
            df = df.rename(columns=dict(zip(df.columns, column_names)))
        if index_col:
            if index_col not in df.columns:
                raise ValueError(f"Index column '{index_col}' not found in DataFrame.")
            df = df.set_index(index_col)

        self.logger.debug("Post-processing complete.", extra=self.logger_extra)
        return df

    def _process_loaded_data(self, df: dd.DataFrame) -> dd.DataFrame:
        field_map = self._backend_params.field_map or {}
        if not isinstance(field_map, dict) or not field_map:
            return df
        if hasattr(df, "npartitions") and df.npartitions == 1 and not len(df.head(1)):
            return df
        self.logger.debug(f"{self.__class__.__name__} is applying rename mapping if/when necessary.", extra=self.logger_extra)
        rename_map = {k: v for k, v in field_map.items() if k in df.columns}
        if rename_map:
            df = df.rename(columns=rename_map)
        return df

    # ---------- sinks ----------
    def save_to_parquet(self, df: dd.DataFrame, **kwargs):
        fs: AbstractFileSystem = kwargs.pop("fs", self.fs)
        path: str = kwargs.pop("parquet_storage_path", self.backend_parquet.parquet_storage_path if self.backend_parquet else None)
        parquet_filename = kwargs.pop("parquet_filename", self.backend_parquet.parquet_filename if self.backend_parquet else None)
        if not parquet_filename:
            raise ValueError("A 'parquet_filename' keyword argument must be provided.")
        if not fs:
            raise ValueError("A filesystem (fs) must be provided to save the parquet file.")
        if not path:
            raise ValueError("A 'parquet_storage_path' keyword argument must be provided.")
        if not self._has_any_rows(df):
            self.logger.warning("Skipping save: The provided DataFrame is empty.", extra=self.logger_extra)
            return

        with ParquetSaver(
            df_result=df,
            parquet_storage_path=path,
            fs=fs,
            debug=self.debug,
            logger=self.logger,
            verbose=self.verbose,
            **kwargs,
        ) as saver:
            saver.save_to_parquet(parquet_filename)

        self.logger.debug(f"Successfully saved '{parquet_filename}' to '{path}'.", extra=self.logger_extra)

    async def asave_to_parquet(self, df: dd.DataFrame, **kwargs):
        await self.emit(event=f"{self.__class__.__name__} save:start", message=f"Saving {len(df)} records to parquet")
        await asyncio.to_thread(self.save_to_parquet, df, **kwargs)
        await self.emit(event=f"{self.__class__.__name__} save:end", message=f"Saved {len(df)} records to parquet")

    def save_to_clickhouse(self, df: dd.DataFrame, **credentials):
        if not self._has_any_rows(df):
            self.logger.warning("Skipping save to ClickHouse: The provided DataFrame is empty.", extra=self.logger_extra)
            return
        with ClickHouseWriter(debug=self.debug, logger=self.logger, verbose=self.verbose, **credentials) as writer:
            writer.save_to_clickhouse(df)
            self.logger.debug("Save to ClickHouse completed.", extra=self.logger_extra)

    async def asave_to_clickhouse(self, df: dd.DataFrame, **credentials):
        await self.emit(event=f"{self.__class__.__name__} save:start", message=f"Saving {len(df)} records to ClickHouse")
        await asyncio.to_thread(self.save_to_clickhouse, df, **credentials)
        await self.emit(event=f"{self.__class__.__name__} save:end", message=f"Saved {len(df)} records to ClickHouse")

    # ---------- period loaders ----------
    def load_period(self, dt_field: str, start: str, end: str, **kwargs):
        final_kwargs = self._prepare_period_filters(dt_field, start, end, **kwargs)
        return self.load(**final_kwargs)

    async def aload_period(self, dt_field: str, start: str, end: str, **kwargs):
        final_kwargs = self._prepare_period_filters(dt_field, start, end, **kwargs)
        return await self.aload(**final_kwargs)

    def _prepare_period_filters(self, dt_field: str, start: str, end: str, **kwargs) -> dict:
        start_date, end_date = pd.to_datetime(start).date(), pd.to_datetime(end).date()
        if start_date > end_date:
            raise ValueError("'start' date cannot be later than 'end' date.")
        field_map = self._backend_params.field_map or {}
        reverse_map = {v: k for k, v in field_map.items()} if field_map else {}
        if len(reverse_map) != len(field_map):
            self.logger.warning("field_map values are not unique; reverse mapping may be unreliable.", extra=self.logger_extra)
        mapped_field = reverse_map.get(dt_field, dt_field)
        if start_date == end_date:
            kwargs[f"{mapped_field}__date"] = start_date
        else:
            kwargs[f"{mapped_field}__date__range"] = [start_date, end_date]
        self.logger.debug(f"Period load generated filters: {kwargs}", extra=self.logger_extra)
        return kwargs

    @staticmethod
    def _has_any_rows(ddf: dd.DataFrame) -> bool:
        try:
            return bool(ddf.head(1, npartitions=-1).shape[0])
        except Exception:
            return False
