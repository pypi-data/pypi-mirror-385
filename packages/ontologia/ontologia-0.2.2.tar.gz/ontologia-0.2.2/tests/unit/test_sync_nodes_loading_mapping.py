from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlmodel import select

import ontologia.application.sync_service as sync_mod
from datacatalog.models import Dataset
from ontologia.application.sync_service import OntologySyncService
from ontologia.domain.metamodels.instances.object_type_data_source import ObjectTypeDataSource
from ontologia.domain.metamodels.types.object_type import ObjectType


def _create_employee_object_type(client: TestClient):
    resp = client.put(
        "/v2/ontologies/default/objectTypes/employee",
        json={
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
        },
    )
    assert resp.status_code == 200


class _StubDF:
    def __init__(self, columns, rows=None):
        self.columns = list(columns)
        if rows is None:
            self.rows = [
                {columns[0]: "e1", columns[1]: "Alice"},
            ]
        else:
            self.rows = rows

    def rename(self, mapping):
        new_columns = [mapping.get(c, c) for c in self.columns]
        new_rows = [{mapping.get(k, k): v for k, v in row.items()} for row in self.rows]
        return _StubDF(new_columns, new_rows)

    def select(self, cols):
        filtered_cols = [c for c in self.columns if c in cols]
        new_rows = [{col: row.get(col) for col in filtered_cols} for row in self.rows]
        return _StubDF(filtered_cols or self.columns, new_rows)

    def lazy(self):
        return _StubLazy(self)


class _StubLazy:
    def __init__(self, df):
        self.df = df
        self.df_rows = list(df.rows)

    def select(self, cols):
        return self


class _StubUnified:
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def to_dicts(self):
        return list(self.rows)

    @property
    def columns(self):
        if not self.rows:
            return []
        return list(self.rows[0].keys())


class _StubConcat:
    def __init__(self, lazies):
        self.lazies = lazies

    def unique(self, subset, keep="last"):
        return self

    def collect(self):
        rows: list[dict[str, object]] = []
        for lazy in self.lazies:
            rows.extend(lazy.df_rows)
        return _StubUnified(rows)


def test_sync_nodes_load_applies_property_mappings(client: TestClient, session):
    # Arrange: create ObjectType via API
    _create_employee_object_type(client)

    # Fetch ObjectType persisted
    ot = session.exec(select(ObjectType).where(ObjectType.api_name == "employee")).one()

    # Create Dataset (duckdb_table) and link
    ds = Dataset(
        service="ontology",
        instance="default",
        api_name="employees_ds",
        display_name="Employees DS",
        source_type="duckdb_table",
        source_identifier="employees_tbl",
        schema_definition={},
    )
    session.add(ds)
    session.commit()
    session.refresh(ds)

    link = ObjectTypeDataSource(
        service="ontology",
        instance="default",
        api_name="emp_link",
        display_name="emp link",
        object_type_rid=ot.rid,
        dataset_rid=ds.rid,
        property_mappings={"emp_id": "id", "name": "name"},
    )
    session.add(link)
    session.commit()

    # Prepare service with kuzu mock
    mock_kuzu = MagicMock()
    svc = OntologySyncService(metadata_session=session, kuzu_conn=mock_kuzu, duckdb_conn=None)

    # Monkeypatch: return stub DF and stub polars concat pipeline
    def _fake_read_dataset(_self, dataset):
        # raw dataset columns before mapping
        return _StubDF(["emp_id", "name"])

    old_read = OntologySyncService._read_dataset
    OntologySyncService._read_dataset = _fake_read_dataset

    old_pl = getattr(sync_mod, "pl", None)
    sync_mod.pl = SimpleNamespace(concat=lambda lazies: _StubConcat(lazies))

    try:
        # Act
        svc.sync_ontology()
    finally:
        # Restore monkeypatches
        OntologySyncService._read_dataset = old_read
        if old_pl is not None:
            sync_mod.pl = old_pl

    merge_calls = [
        call.args[0]
        for call in mock_kuzu.execute.call_args_list
        if call.args and "MERGE (o:Object" in str(call.args[0])
    ]
    assert merge_calls, "expected MERGE call into Object node"
    payload = merge_calls[-1]
    assert '"id"' in payload
    assert '"emp_id"' not in payload
