# Environment & Feature Flags

Centralized reference for configuration knobs. Defaults live in `ontologia.toml`; environment variables act as overrides for automation and ad-hoc workflows.

## Manifest (`ontologia.toml`)

```toml
[features]
use_unified_graph = true
use_graph_reads = true
use_graph_writes = false
use_temporal_actions = false
```

At runtime the platform reads these settings via `ontologia.config`. Setting the corresponding environment variable (`USE_UNIFIED_GRAPH`, `USE_GRAPH_READS`, `USE_GRAPH_WRITES`, `USE_TEMPORAL_ACTIONS`) temporarily overrides the manifest value.

## Core

- `KUZU_DB_PATH`
  - Path to the Kùzu database (directory).
  - Default: `instance_graph.kuzu` (see `KuzuDBRepository`).

- `DUCKDB_PATH`
  - Path to the DuckDB file used by the sync runner.

## Graph Reads/Writes

- Graph reads are "graph-first" automatically when `[features.use_graph_reads]` is true (default). Repositories fall back to SQLModel if the graph is unavailable.

- `features.use_graph_writes`
  - Enables write-through to Kùzu on object/link mutations. SQL remains the source of truth.
  - Override with `USE_GRAPH_WRITES=1` (or `0`).

- `features.use_unified_graph`
  - Enables the unified Object node model with JSON `properties` and `labels`.
  - Benefits: interface-based listing (`/objects/{Interface}`) uses a single graph query; simplified schema creation during sync.
  - Unified mode is always enforced. Setting `USE_UNIFIED_GRAPH=0` is ignored and logs a warning.
  - Use `ontologia graph reset --yes` to drop the existing Kùzu storage before a fresh sync.

## Sync

- `SYNC_ENABLE_COPY_RELS`
  - When `1`/`true`, enable fast `COPY ... FROM duckdb.<table>` for relationship loading in `OntologySyncService._load_rels_into_graph()`.

## Logging

- `LOG_LEVEL`
  - Standard Python logging level (e.g., `INFO`, `DEBUG`).
  - Traversal logs (`InstancesService.get_linked_objects`) include source, limits, count, and duration.

## Temporal (Actions)

- `USE_TEMPORAL_ACTIONS`
  - When `1`/`true`, the Actions endpoints use Temporal workflows instead of synchronous execution.
  - Affects:
    - `POST /v2/ontologies/{ontology}/objects/{objType}/{pk}/actions/{action}/execute` (awaits workflow result)
    - `POST /v2/ontologies/{ontology}/objects/{objType}/{pk}/actions/{action}/start` (fire-and-forget)
    - `GET  /v2/ontologies/{ontology}/actions/runs/{workflowId}` (status)

- `TEMPORAL_ADDRESS`
  - Frontend host:port of Temporal. Default: `127.0.0.1:7233`.

- `TEMPORAL_NAMESPACE`
  - Temporal namespace. Default: `default`.

- `TEMPORAL_TASK_QUEUE`
  - Task queue used by the worker. Default: `actions`.
