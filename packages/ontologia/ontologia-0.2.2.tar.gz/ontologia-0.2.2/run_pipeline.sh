#!/usr/bin/env bash
set -euo pipefail

echo "=== Ontologia Data Pipeline ==="

: "${ONTOLOGIA_CONFIG_ROOT:=$(pwd)}"
: "${DUCKDB_PATH:=$(pwd)/data.duckdb}"

echo "Config root: ${ONTOLOGIA_CONFIG_ROOT}"
echo "DuckDB path: ${DUCKDB_PATH}"

ONTOLOGIA_CONFIG_ROOT="${ONTOLOGIA_CONFIG_ROOT}" \
DUCKDB_PATH="${DUCKDB_PATH}" \
uv run ontologia-cli pipeline run "$@"

echo "=== Done ==="
