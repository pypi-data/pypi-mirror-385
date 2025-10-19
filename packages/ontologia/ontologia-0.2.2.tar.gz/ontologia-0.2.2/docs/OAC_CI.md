# Ontology as Code – CI Integration

This guide explains how to run the Ontologia OaC checks in CI and how to interpret results.

## Goals

- Validate YAML definitions against API schemas.
- Diff local YAML vs. server state; fail on dangerous plans.
- Keep PRs safe by surfacing dependency and impact summaries.

## Example Workflow (GitHub Actions)

A ready-to-use workflow is included at `.github/workflows/oac.yml`.

Key steps:

- Checkout repository
- Setup Python and `uv`
- Install dependencies with `uv sync --dev`
- Start API locally (Uvicorn)
- Run CLI `validate` and `diff` (with `--fail-on-dangerous`)

```yaml
name: Ontology as Code

on:
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  validate-and-diff:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Setup uv
        uses: astral-sh/setup-uv@v3

      - name: Install dependencies
        run: uv sync --dev

      - name: Start API
        run: |
          nohup uv run uvicorn api.main:app --host 127.0.0.1 --port 8000 >/dev/null 2>&1 &
          for i in {1..30}; do
            if curl -sf http://127.0.0.1:8000/health > /dev/null; then
              echo "API ready"; break; fi
            sleep 1
          done

      - name: OAC Validate
        run: uv run ontologia-cli validate --dir example_project/ontology --host http://127.0.0.1:8000 --ontology default

      - name: OAC Diff (fail on dangerous)
        run: uv run ontologia-cli diff --dir example_project/ontology --host http://127.0.0.1:8000 --ontology default --fail-on-dangerous
```

Notes:

- If you have multiple ontologies/environments, parameterize `--ontology` and API `--host` via repository or environment variables.
- To see dependency/impact summaries in the job log, add `--deps --impact` to the `diff` step.

## Dangerous Operations

The CLI marks certain operations as “dangerous” and the workflow fails when they are detected (via `--fail-on-dangerous`):

- Changing an `ObjectType.primaryKey`.
- Deleting `ObjectType` or `LinkType` present only in server.
- Changing endpoints (`fromObjectType`/`toObjectType`) of a `LinkType`.

Server-side guards in `MetamodelService` also prevent destructive changes when data exists:

- Cannot delete an `ObjectType` that is referenced by `LinkType`s or that has instances.
- Cannot change `ObjectType.primaryKey` when instances exist.
- Cannot change `LinkType` endpoints when links exist.
- Cannot delete a `LinkType` when links exist.

## Optional Flags

- `--deps` (diff): print which `LinkType`s reference changed `ObjectType`s.
- `--impact` (diff): print instance counts for affected object types via `POST /analytics/aggregate`.
- `--allow-destructive` (apply): required to execute deletes.

## Local Parity

To reproduce CI locally:

```bash
# Start API
uv run uvicorn api.main:app --host 127.0.0.1 --port 8000

# In another terminal
uv run ontologia-cli validate --dir example_project/ontology --host http://127.0.0.1:8000 --ontology default
uv run ontologia-cli diff --dir example_project/ontology --host http://127.0.0.1:8000 --ontology default --fail-on-dangerous --deps --impact
```

## Troubleshooting

- CLI not found or imports fail in dev: prefer module invocation:

```bash
uv run python -m ontologia_cli.main diff --dir example_project/ontology --host http://127.0.0.1:8000 --ontology default
```

- Empty `example_project/ontology/` directory: `validate` passes but `diff` will propose deletes against a populated server; create YAMLs under `example_project/ontology/object_types/` and `example_project/ontology/link_types/`.
- Action resolution warnings in local editor (e.g., `actions/checkout@v4`): these are editor heuristics and do not affect GitHub-hosted runners.
