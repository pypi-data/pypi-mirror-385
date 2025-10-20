# DBT Guide (Phase 1)

This guide explains how to run and work with the DBT project used for Ontologia's transformations.

## Structure

- Project: `example_project/dbt_project/`
  - `dbt_project.yml`: DBT configuration (models/materializations)
  - `profiles.yml`: DBT profile. Uses `DUCKDB_PATH` env var for the DuckDB database path.
  - `models/`
    - `bronze/`: raw sources (declared via `sources`)
    - `silver/`: staging models (cleaning/standardization)
    - `gold/`: models consumed by the sync service

## Prerequisites

- Install dev dependencies:

```bash
uv sync --dev
```

- Set the database path:

```bash
export DUCKDB_PATH=$(pwd)/data.duckdb
```

## Bootstrap & Build

Prepare raw tables and build the pipeline:

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

What it does:
- Creates `employees_tbl` and `works_for_tbl` in DuckDB if missing (with seed rows)
- Runs `dbt deps` and `dbt build` (Bronze → Silver → Gold)
- Runs the sync loader to populate KùzuDB from Gold models

## Running DBT directly

From the project root:

```bash
cd example_project/dbt_project
export DBT_PROFILES_DIR=$(pwd)
uv run dbt deps
uv run dbt build
```

## Data Quality

- Gold `ontologia_employees`:
  - `id`: `unique`, `not_null`
- Gold `ontologia_works_for`:
  - `emp_id`: `not_null`
  - `company_id`: `not_null`

Add more tests as needed in `models/gold/schema.yml`.

## Docs & Lineage

Generate and serve your DBT docs:

```bash
cd example_project/dbt_project
export DBT_PROFILES_DIR=$(pwd)
uv run dbt docs generate
uv run dbt docs serve  # local server
```

## Notes

- To assume Gold schema in the sync and skip legacy renames:

```bash
export SYNC_ASSUME_GOLD_SCHEMA=1
```

- Unified graph mode (obrigatório): mantenha `features.use_unified_graph = true` em `ontologia.toml` (o padrão). Overrides que tentam desativar são ignorados.
