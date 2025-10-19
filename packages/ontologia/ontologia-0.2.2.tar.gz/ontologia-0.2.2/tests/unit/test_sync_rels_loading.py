from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from datacatalog.models import Dataset
from ontologia.application.sync_service import OntologySyncService


def _create_basic_types(client: TestClient):
    # employee
    resp_emp = client.put(
        "/v2/ontologies/default/objectTypes/employee",
        json={
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
            },
        },
    )
    assert resp_emp.status_code == 200

    # company
    resp_co = client.put(
        "/v2/ontologies/default/objectTypes/company",
        json={
            "displayName": "Company",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
            },
        },
    )
    assert resp_co.status_code == 200

    # works_for link
    resp_link = client.put(
        "/v2/ontologies/default/linkTypes/works_for",
        json={
            "displayName": "Works For",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employees"},
        },
    )
    assert resp_link.status_code == 200


def test_sync_rels_loading_uses_conventional_dataset(client: TestClient, session):
    _create_basic_types(client)

    # Create a conventional dataset for relations: works_for_rels
    ds = Dataset(
        service="ontology",
        instance="default",
        api_name="works_for_rels",
        display_name="works_for relations",
        source_type="duckdb_table",
        source_identifier="works_for_rel_tbl",
        schema_definition={},
    )
    session.add(ds)
    session.commit()

    # Prepare mocked kuzu and patched read to simulate available data
    mock_kuzu = MagicMock()

    def _fake_read_dataset(_self, dataset):
        # Presence is enough; columns are not strictly validated in current impl
        return object()  # non-None sentinel

    old_read = OntologySyncService._read_dataset
    OntologySyncService._read_dataset = _fake_read_dataset

    try:
        svc = OntologySyncService(metadata_session=session, kuzu_conn=mock_kuzu, duckdb_conn=None)
        svc.sync_ontology()
    finally:
        OntologySyncService._read_dataset = old_read

    # Assert an execute call was issued for rels loading of works_for
    executed_cmds = [str(call.args[0]) for call in mock_kuzu.execute.call_args_list]
    assert any(
        "loading rels for works_for" in cmd and "works_for_rels" in cmd for cmd in executed_cmds
    )
