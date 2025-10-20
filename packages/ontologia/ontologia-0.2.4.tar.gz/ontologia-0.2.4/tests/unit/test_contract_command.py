from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture()
def fake_duckdb(tmp_path: Path):
    db_path = tmp_path / "data.duckdb"
    db_path.touch()

    class _DummyConnection:
        def __init__(self, rows):
            self.rows = rows

        def execute(self, _query):  # noqa: D401
            mock = MagicMock()
            mock.fetchall.return_value = self.rows
            return mock

        def close(self) -> None:  # noqa: D401
            return None

    return db_path, _DummyConnection


class DummyDataset:
    def __init__(self, source_identifier: str):
        self.source_type = "duckdb_table"
        self.source_identifier = source_identifier


class DummyDataSource:
    def __init__(self, dataset: DummyDataset, property_mappings: dict[str, str] | None = None):
        self.dataset = dataset
        self.dataset_branch = None
        self.property_mappings = property_mappings or {}


class DummySession:
    def __init__(self, object_types):
        self._object_types = list(object_types)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def exec(self, _statement):
        return SimpleNamespace(all=lambda: list(self._object_types))

    def close(self):
        return None


@patch("ontologia_cli.main.load_config")
def test_contract_command_failure_on_missing_duckdb_config(mock_load_config, tmp_path):
    from ontologia_cli.main import test_contract_command

    mock_cfg = MagicMock()
    mock_cfg.data.duckdb_path = str(tmp_path / "missing.duckdb")
    mock_cfg.api.ontology = "default"
    mock_load_config.return_value = mock_cfg

    defs_dir = tmp_path / "object_types"
    defs_dir.mkdir(parents=True, exist_ok=True)
    (defs_dir / "customer.yaml").write_text(
        """
apiName: customer
displayName: Customer
primaryKey: id
properties:
  id:
    dataType: string
    displayName: ID
    required: true
""",
        encoding="utf-8",
    )
    with patch("sqlmodel.Session", return_value=DummySession([])):
        exit_code = test_contract_command(str(tmp_path))

    assert exit_code == 1


@patch("ontologia_cli.main.load_config")
def test_contract_command_missing_columns(mock_load_config, fake_duckdb, tmp_path):
    from ontologia_cli.main import test_contract_command

    db_path, dummy_conn_cls = fake_duckdb
    temp_cfg = MagicMock()
    temp_cfg.data.duckdb_path = str(db_path)
    temp_cfg.api.ontology = "default"
    mock_load_config.return_value = temp_cfg

    dataset = DummyDataset("analytics.customer_gold")
    object_type = SimpleNamespace(api_name="customer", data_sources=[DummyDataSource(dataset)])
    defs_dir = tmp_path / "object_types"
    defs_dir.mkdir(parents=True, exist_ok=True)
    (defs_dir / "customer.yaml").write_text(
        """
apiName: customer
displayName: Customer
primaryKey: id
properties:
  id:
    dataType: string
    displayName: ID
    required: true
  name:
    dataType: string
    displayName: Name
    required: true
""",
        encoding="utf-8",
    )

    duckdb_stub = SimpleNamespace(
        connect=MagicMock(return_value=dummy_conn_cls(rows=[("id", "VARCHAR")])),
        Error=Exception,
        DuckDBPyConnection=object,
    )

    with (
        patch("sqlmodel.Session", return_value=DummySession([object_type])),
        patch.dict("sys.modules", {"duckdb": duckdb_stub}),
    ):
        exit_code = test_contract_command(str(tmp_path), duckdb_path=str(db_path))

    assert exit_code == 1


@patch("ontologia_cli.main.load_config")
def test_contract_command_quality_checks(mock_load_config, fake_duckdb, tmp_path):
    from ontologia_cli.main import test_contract_command

    db_path, dummy_conn_cls = fake_duckdb
    mock_cfg = MagicMock()
    mock_cfg.data.duckdb_path = str(db_path)
    mock_cfg.api.ontology = "default"
    mock_load_config.return_value = mock_cfg

    dataset = DummyDataset("analytics.customer_gold")
    data_source = DummyDataSource(dataset)
    object_type = SimpleNamespace(api_name="customer", data_sources=[data_source])
    defs_dir = tmp_path / "object_types"
    defs_dir.mkdir(parents=True, exist_ok=True)
    (defs_dir / "customer.yaml").write_text(
        """
apiName: customer
displayName: Customer
primaryKey: id
properties:
  id:
    dataType: string
    displayName: ID
    required: true
  name:
    dataType: string
    displayName: Name
    required: true
    qualityChecks:
      - not_null
""",
        encoding="utf-8",
    )

    duckdb_rows = [("id", "VARCHAR"), ("name", "VARCHAR")]

    duckdb_stub = SimpleNamespace(
        connect=MagicMock(return_value=dummy_conn_cls(rows=duckdb_rows)),
        Error=Exception,
        DuckDBPyConnection=object,
    )

    with (
        patch("sqlmodel.Session", return_value=DummySession([object_type])),
        patch.dict("sys.modules", {"duckdb": duckdb_stub}),
    ):
        exit_code = test_contract_command(str(tmp_path), duckdb_path=str(db_path))
        assert exit_code == 0
