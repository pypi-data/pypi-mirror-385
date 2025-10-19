# Sync Service Overview

High-level summary of the ontology synchronization process that materializes the graph in KùzuDB.

See also: `../SYNC_SERVICE_GUIDE.md` for a deep dive and diagrams.

## What It Does

- Reads metamodel from the Control Plane (SQLModel): `ObjectType`, `LinkType`, `Dataset`, `ObjectTypeDataSource`.
- Extracts data from the Raw Data Plane (DuckDB or Parquet) via Polars.
- Transforms and unifies rows according to the semantic model.
- Loads into the Semantic Plane (KùzuDB):
  - Nodes (ObjectType instances)
  - Relationships (LinkType instances)

## How It Works (Steps)

`ontologia/application/sync_service.py` (class `OntologySyncService`):

1. `_build_graph_schema()`
   - Creates NODE and REL TABLES in Kùzu using metadata.
2. `_attach_duckdb()`
   - Optionally attaches a DuckDB database for direct `COPY` sources.
3. `_load_nodes_into_graph()`
   - Reads datasets for each `ObjectType` via Polars, applies mappings, de-duplicates by PK, and calls `kuzu.load_from_polars`.
4. `_load_rels_into_graph()`
   - Uses `LinkType.backing_dataset_rid` + mappings to bulk-load edges.
   - When `SYNC_ENABLE_COPY_RELS=1`, executes a fast `COPY ... FROM duckdb.<table> (FROM <from_col> TO <to_col> [PROPERTIES (...)])`.
   - Fallback path reads the dataset and logs a command marker, recording metrics.

## Running the Sync Runner

`scripts/main_sync.py` can bootstrap a minimal control plane and run a sync end-to-end.

```bash
# Optional: DuckDB file for data sources
export DUCKDB_PATH=analytics.duckdb

# Bootstrap example metamodel and datasets
export SYNC_SETUP=1

# Optional: accelerate relationship loading
export SYNC_ENABLE_COPY_RELS=1

uv run python scripts/main_sync.py
```

After running, if KùzuDB is installed, the graph schema and data will be ready for traversal queries.

## Environment Flags

- `KUZU_DB_PATH`: Path to Kùzu database dir
- `DUCKDB_PATH`: Path to DuckDB file (used by sync)
- `SYNC_SETUP`: Bootstrap example metamodel/datasets in runner
- `SYNC_ENABLE_COPY_RELS`: Use COPY for relationships in sync

## Validating Results

- API traversal endpoint: `GET /v2/ontologies/{ontology}/objects/{ot}/{pk}/{lt}`
- Direct graph queries via repositories:
  - `GraphInstancesRepository.get_linked_objects()`
  - `GraphLinkedObjectsRepository.list_edges()`

Refer to tests:
- `tests/integration/test_sync_rels_loading.py` (COPY path validation)
- `tests/unit/test_sync_nodes_loading.py` (node loading path)
