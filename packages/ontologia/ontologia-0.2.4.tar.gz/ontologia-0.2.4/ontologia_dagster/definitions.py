"""
Dagster job for Ontologia pipeline.

This defines a minimal job that executes:
1) prepare_raw (DuckDB bootstrap)
2) dbt deps + dbt build (project: example_project/dbt_project/)
3) graph sync (OntologySyncService)

Run locally:
- UI:     uv run dagster dev -m ontologia_dagster
- Single: DUCKDB_PATH=$(pwd)/data.duckdb uv run dagster job execute -m ontologia_dagster -j pipeline_job
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from dagster import (
    Definitions,
    In,
    Nothing,
    Out,
    ScheduleDefinition,
    in_process_executor,
    job,
    op,
)
from dagster_dbt import DbtCliResource

# Resolve DBT project directory relative to this file
DBT_PROJECT_DIR = Path(__file__).resolve().parent.parent / "example_project" / "dbt_project"

# Dagster resource to run DBT via CLI
# Requires dbt + adapter (dbt-duckdb) installed in the environment
DBT = DbtCliResource(
    project_dir=os.fspath(DBT_PROJECT_DIR), profiles_dir=os.fspath(DBT_PROJECT_DIR)
)


@op(config_schema={"duckdb_path": str | None}, out={"done": Out(Nothing)})
def prepare_raw_op(context) -> None:
    """Create and seed minimal raw DuckDB tables used by DBT."""
    # Optional override of DUCKDB_PATH via config
    duckdb_path = (context.op_config or {}).get("duckdb_path")
    if duckdb_path:
        os.environ["DUCKDB_PATH"] = duckdb_path
    # Dynamically load the script by absolute path to avoid sys.path issues
    repo_root = Path(__file__).resolve().parent.parent
    script_path = repo_root / "scripts" / "prepare_duckdb_raw.py"
    spec = importlib.util.spec_from_file_location("prepare_duckdb_raw", script_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    module.main()
    # Signal completion without data
    return None


@op(
    ins={"start": In(Nothing)},
    out={"done": Out(Nothing)},
    required_resource_keys={"dbt"},
    config_schema={"duckdb_path": str | None},
)
def dbt_build_op(context) -> None:
    """Run `dbt deps` and `dbt build` with proper profiles dir and DUCKDB_PATH."""
    duckdb_path = (context.op_config or {}).get("duckdb_path")
    if duckdb_path:
        os.environ["DUCKDB_PATH"] = duckdb_path
    context.log.info("Running dbt deps…")
    context.resources.dbt.cli(["deps"], context=context).wait()
    context.log.info("Running dbt build…")
    context.resources.dbt.cli(["build"], context=context).wait()
    return None


@op(ins={"start": In(Nothing)}, config_schema={"duckdb_path": str | None})
def sync_op(context) -> None:
    """Load GOLD tables into the Kùzu graph using OntologySyncService."""
    # Dynamically load runner to avoid module path issues
    repo_root = Path(__file__).resolve().parent.parent
    # Ensure repo root is importable so 'api' package resolves
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    script_path = repo_root / "scripts" / "main_sync.py"
    spec = importlib.util.spec_from_file_location("main_sync", script_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    duckdb_path = (context.op_config or {}).get("duckdb_path") or os.getenv("DUCKDB_PATH")
    module.run_sync(duckdb_path=duckdb_path)


@job(executor_def=in_process_executor)
def pipeline_job():
    # Order: prepare → dbt → sync (dependencies via Nothing)
    prepared = prepare_raw_op()
    built = dbt_build_op(start=prepared)
    sync_op(start=built)


pipeline_daily = ScheduleDefinition(
    name="pipeline_daily",
    job=pipeline_job,
    cron_schedule="0 2 * * *",  # daily at 02:00
)


defs = Definitions(jobs=[pipeline_job], resources={"dbt": DBT}, schedules=[pipeline_daily])
