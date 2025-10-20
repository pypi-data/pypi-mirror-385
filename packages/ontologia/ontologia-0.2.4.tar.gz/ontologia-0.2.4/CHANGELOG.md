## [0.2.2] - 2025-10-10

- Added: Temporal Actions endpoints (behind `USE_TEMPORAL_ACTIONS`):
  - Blocking execute via Temporal workflow: `POST /v2/ontologies/{ontology}/objects/{type}/{pk}/actions/{action}/execute`
  - Fire-and-forget start: `POST /v2/ontologies/{ontology}/objects/{type}/{pk}/actions/{action}/start`
  - Status: `GET /v2/ontologies/{ontology}/actions/runs/{workflowId}`
  - Cancel: `POST /v2/ontologies/{ontology}/actions/runs/{workflowId}:cancel`
- Added: Centralized configuration via Pydantic Settings (`api/core/settings.py`).
- Added: Temporal Web UI service in `docker-compose.temporal.yml` (http://localhost:8233).
- Added: Dagster daily schedule `pipeline_daily` for `pipeline_job`.
- Improved: Temporal activity retry policy in `ActionWorkflow`.
- Docs: New/updated guides (`docs/ACTIONS.md`, `docs/ENVIRONMENT.md`, `README.md`) for Temporal usage.
- Tests: Extended integration tests for Temporal start/status/cancel (suite now 54 passing).

# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2025-10-05

- Added: Advanced search endpoint `POST /v2/ontologies/{ontology}/objects/{type}/search` with filters (`eq`, `ne`, `lt`, `lte`, `gt`, `gte`, `contains`, `in`), `orderBy`, and pagination.
- Added: Bulk load endpoints:
  - Objects: `POST /v2/ontologies/{ontology}/objects/{type}/load` (upsert multiple objects)
  - Links: `POST /v2/ontologies/{ontology}/links/{linkType}/load` (create/delete multiple links)
- Added: Analytics endpoint `POST /v2/ontologies/{ontology}/aggregate` supporting `COUNT`, `SUM`, `AVG` with optional `groupBy` and `where` (SQL fallback; graph path planned).
- Docs: Updated `docs/API_REFERENCE.md` and `docs/ONBOARDING.md` with examples for search, bulk, and analytics.
- Tests: Integration tests added for search, bulk, and aggregate; full suite passes (36).

## [0.2.0] - 2025-10-05

- Traversal endpoint implemented: `GET /v2/ontologies/{ontology}/objects/{type}/{pk}/{linkType}` with pagination and graph-backed reads (when `USE_GRAPH_READS=1`) plus SQL fallback.
- Repo/docs reorg: centralized docs under `docs/` (guides, reports, ADR), onboarding, architecture, API reference, environment, sync.
- Examples: Added `examples/library_quickstart.py` and `examples/api_quickstart.py`; updated `examples/README.md`.
- Hygiene: Ignored DB artifacts; moved legacy demo tests to `examples/legacy/`.
- Tests: Suite green (33) at the time of tagging.

