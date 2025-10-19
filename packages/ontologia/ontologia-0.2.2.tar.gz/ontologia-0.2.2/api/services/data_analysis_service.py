"""Utility service for profiling tabular and remote data sources."""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx

_TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


class DataAnalysisService:
    """Provide lightweight statistical profiling for tabular data files."""

    SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".parquet"}

    def profile_source(self, source_path: Path, sample_size: int = 100) -> dict[str, Any]:
        """Return statistics about the given tabular data source.

        Args:
            source_path: Absolute path to the data file.
            sample_size: Maximum number of rows to load when profiling.

        Returns:
            A dictionary with summary information that can be consumed by LLM agents.
        """

        if sample_size <= 0:
            raise ValueError("sample_size must be a positive integer")

        ext = source_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension '{ext}'. Supported extensions: {sorted(self.SUPPORTED_EXTENSIONS)}"
            )

        if not source_path.exists():
            raise FileNotFoundError(f"Data source '{source_path}' not found")

        frame, backend = self._read_frame(source_path, ext, sample_size)
        height = int(len(frame))

        columns: list[dict[str, Any]]
        if backend == "polars":
            columns = self._profile_polars(frame, height)
        elif backend == "python":
            columns = self._profile_python(frame, height)
        else:
            columns = self._profile_pandas(frame, height)

        return {
            "source_path": str(source_path),
            "rows_profiled": height,
            "columns": columns,
        }

    def _read_frame(self, path: Path, extension: str, sample_size: int) -> tuple[Any, str]:
        if extension == ".parquet":
            try:
                import polars as pl

                df = pl.read_parquet(path)
                return df.slice(0, min(sample_size, df.height)), "polars"
            except ImportError:
                try:
                    import pandas as pd

                    df = pd.read_parquet(path)
                    return df.head(sample_size), "pandas"
                except ImportError as exc:  # pragma: no cover - guarded by tests using CSV inputs
                    raise RuntimeError(
                        "Parquet profiling requires either Polars or Pandas. Install one of them in the environment."
                    ) from exc

        if extension in {".csv", ".tsv"}:
            sep = "\t" if extension == ".tsv" else ","
            try:
                import polars as pl

                return pl.read_csv(path, n_rows=sample_size, separator=sep), "polars"
            except ImportError:
                import csv

                rows: list[dict[str, Any]] = []
                with path.open("r", encoding="utf-8", newline="") as fh:
                    reader = csv.DictReader(fh, delimiter=sep)
                    for i, row in enumerate(reader):
                        rows.append(dict(row))
                        if i + 1 >= sample_size:
                            break
                return rows, "python"

        raise ValueError(f"Unsupported extension '{extension}'")

    def _profile_polars(self, frame, height: int) -> list[dict[str, Any]]:
        columns: list[dict[str, Any]] = []
        for col_name in frame.columns:
            series = frame[col_name]
            non_null = series.drop_nulls()
            unique_count = int(series.n_unique())
            null_count = height - int(non_null.len())
            example_values = non_null.head(min(5, non_null.len())).to_list()
            is_highly_unique = bool(height and unique_count / max(height, 1) >= 0.95)

            columns.append(
                {
                    "name": col_name,
                    "inferred_type": str(series.dtype),
                    "unique_count_in_sample": unique_count,
                    "null_count_in_sample": null_count,
                    "is_highly_unique": is_highly_unique,
                    "example_values": example_values,
                }
            )
        return columns

    def _profile_pandas(self, frame, height: int) -> list[dict[str, Any]]:
        import pandas as pd  # noqa: F401 - imported for type completeness

        columns: list[dict[str, Any]] = []
        for col_name in frame.columns:
            series = frame[col_name]
            null_count = int(series.isna().sum())
            unique_count = int(series.nunique(dropna=True))
            non_null = series.dropna()
            example_values = list(non_null.head(5))
            is_highly_unique = bool(height and unique_count / max(height, 1) >= 0.95)

            columns.append(
                {
                    "name": col_name,
                    "inferred_type": str(series.dtype),
                    "unique_count_in_sample": unique_count,
                    "null_count_in_sample": null_count,
                    "is_highly_unique": is_highly_unique,
                    "example_values": example_values,
                }
            )
        return columns

    def _profile_python(
        self,
        rows: list[dict[str, Any]],
        height: int,
        column_names: Sequence[str] | None = None,
    ) -> list[dict[str, Any]]:
        if not rows and not column_names:
            return []

        column_names = list(column_names or rows[0].keys())
        columns: list[dict[str, Any]] = []
        for col_name in column_names:
            values = [row.get(col_name) for row in rows]
            non_null = [v for v in values if v not in (None, "")]
            unique_values = set(non_null)
            null_count = len(values) - len(non_null)
            example_values = non_null[:5]
            inferred_type = self._infer_python_type(non_null)
            is_highly_unique = bool(height and len(unique_values) / max(height, 1) >= 0.95)

            columns.append(
                {
                    "name": col_name,
                    "inferred_type": inferred_type,
                    "unique_count_in_sample": len(unique_values),
                    "null_count_in_sample": null_count,
                    "is_highly_unique": is_highly_unique,
                    "example_values": example_values,
                }
            )
        return columns

    @staticmethod
    def _infer_python_type(values: list[Any]) -> str:
        if not values:
            return "unknown"

        def is_bool(v: Any) -> bool:
            if isinstance(v, bool):
                return True
            if isinstance(v, str):
                return v.lower() in {"true", "false"}
            return False

        def is_int(value: Any) -> bool:
            if isinstance(value, bool):
                return False
            if isinstance(value, int):
                return True
            if isinstance(value, str):
                try:
                    parsed = float(value)
                except (TypeError, ValueError):
                    return False
                return parsed.is_integer()
            return False

        def is_float(value: Any) -> bool:
            if isinstance(value, bool):
                return False
            if isinstance(value, float):
                return True
            if isinstance(value, str):
                try:
                    float(value)
                    return True
                except (TypeError, ValueError):
                    return False
            return False

        if all(is_bool(v) for v in values):
            return "bool"
        if all(is_int(v) for v in values):
            return "int"
        if all(is_float(v) for v in values):
            return "float"
        return "str"

    def profile_sql_table(
        self,
        connection_url: str,
        table_name: str,
        *,
        sample_size: int = 100,
    ) -> dict[str, Any]:
        """Profile a relational database table using SQLAlchemy."""

        if sample_size <= 0:
            raise ValueError("sample_size must be a positive integer")
        if not table_name or not _TABLE_NAME_PATTERN.match(table_name.replace(".", "_")):
            raise ValueError("table_name contains unsupported characters")

        try:  # pragma: no cover - import guard (exercised via sqlite in tests)
            from sqlalchemy import MetaData, Table, create_engine, inspect, select
            from sqlalchemy.exc import NoSuchTableError
        except ImportError as exc:  # pragma: no cover - optional dependency guard
            raise RuntimeError(
                "SQL profiling requires SQLAlchemy. Install it with `uv add sqlalchemy`."
            ) from exc

        schema: str | None = None
        table_id = table_name
        if "." in table_name:
            schema, table_id = table_name.rsplit(".", 1)

        engine = create_engine(connection_url)
        metadata = MetaData()
        try:
            table = Table(table_id, metadata, schema=schema, autoload_with=engine)
        except NoSuchTableError as exc:
            engine.dispose()
            raise ValueError(f"Table '{table_name}' not found") from exc

        inspector = inspect(engine)
        column_info = inspector.get_columns(table_id, schema=schema)

        stmt = select(table).limit(sample_size)
        rows: list[dict[str, Any]] = []
        with engine.connect() as conn:
            result = conn.execute(stmt)
            rows = [dict(row) for row in result.mappings()]
        engine.dispose()

        height = len(rows)
        columns = self._profile_python(
            rows, height, column_names=[col["name"] for col in column_info]
        )
        return {
            "source": "sql_table",
            "connection_url": connection_url,
            "table_name": table_name,
            "rows_profiled": height,
            "columns": columns,
        }

    def profile_rest_endpoint(
        self,
        url: str,
        *,
        sample_size: int = 100,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        array_path: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> dict[str, Any]:
        """Profile JSON array payloads returned by REST endpoints."""

        if sample_size <= 0:
            raise ValueError("sample_size must be a positive integer")
        verb = method.upper()
        if verb not in {"GET", "POST"}:
            raise ValueError("method must be GET or POST")

        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.request(verb, url, headers=headers)
            response.raise_for_status()
            payload = response.json()

        data: Any = payload
        if array_path:
            for part in array_path.split("."):
                if isinstance(data, dict) and part in data:
                    data = data[part]
                else:
                    raise ValueError(f"array_path '{array_path}' did not resolve to data")

        if not isinstance(data, list):
            raise ValueError(
                "Endpoint response must be a JSON array or resolve to one via array_path"
            )

        rows: list[dict[str, Any]] = []
        for item in data[:sample_size]:
            if not isinstance(item, dict):
                raise ValueError("JSON array items must be objects")
            rows.append(dict(item))

        height = len(rows)
        columns = self._profile_python(rows, height)
        return {
            "source": "rest_endpoint",
            "url": url,
            "method": verb,
            "rows_profiled": height,
            "columns": columns,
        }
