#!/usr/bin/env python3
"""
Bootstrap minimal raw DuckDB tables used by the DBT project.

Tables created (if not exists):
- employees_tbl(emp_id TEXT, name TEXT)
- works_for_tbl(emp_id TEXT, company_id TEXT)

Reads DUCKDB_PATH from the environment or defaults to ./data.duckdb.
"""
from __future__ import annotations

import os
from pathlib import Path

import duckdb

from ontologia.config import load_config


def main() -> None:
    config = load_config(Path(os.getenv("ONTOLOGIA_CONFIG_ROOT", Path.cwd())))
    db_path = os.getenv(
        "DUCKDB_PATH",
        os.path.abspath(config.data.duckdb_path),
    )
    con = duckdb.connect(db_path)
    try:
        # Ensure schema matches DBT source schema ('raw_data')
        con.execute("create schema if not exists raw_data;")
        con.execute(
            """
            create table if not exists raw_data.employees_tbl (
              emp_id text,
              name text
            );
            """
        )
        con.execute(
            """
            create table if not exists raw_data.works_for_tbl (
              emp_id text,
              company_id text
            );
            """
        )
        # Seed minimal rows if tables are empty
        emp_row = con.execute("select count(*) from raw_data.employees_tbl").fetchone()
        emp_count = emp_row[0] if emp_row else 0
        if emp_count == 0:
            con.execute(
                "insert into raw_data.employees_tbl (emp_id, name) values (?, ?), (?, ?)",
                ["e1", "Alice", "e2", "Bob"],
            )
        wf_row = con.execute("select count(*) from raw_data.works_for_tbl").fetchone()
        wf_count = wf_row[0] if wf_row else 0
        if wf_count == 0:
            con.execute(
                "insert into raw_data.works_for_tbl (emp_id, company_id) values (?, ?), (?, ?)",
                ["e1", "c1", "e2", "c1"],
            )
    finally:
        con.close()


if __name__ == "__main__":
    main()
