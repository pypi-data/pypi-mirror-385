from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from ontologia.application.sync_service import OntologySyncService


def _create_basic_object_types(client: TestClient):
    # employee
    resp_emp = client.put(
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
    assert resp_emp.status_code == 200

    # company
    resp_co = client.put(
        "/v2/ontologies/default/objectTypes/company",
        json={
            "displayName": "Company",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
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


def test_sync_builds_kuzu_schema_calls_execute(client: TestClient, session):
    """
    Smoke test: given two ObjectTypes and a LinkType, the SyncService should
    issue CREATE statements against the (mocked) Kùzu connection without errors.
    """
    _create_basic_object_types(client)

    mock_kuzu = MagicMock()

    svc = OntologySyncService(metadata_session=session, kuzu_conn=mock_kuzu, duckdb_conn=None)
    metrics = (
        svc.sync_ontology()
    )  # No DuckDB path; only schema build and node load (no Kùzu load without Polars)

    # Aggregate executed Cypher for assertions
    executed = "\n".join(str(call.args[0]) for call in mock_kuzu.execute.call_args_list)

    assert "CREATE NODE TABLE Object" in executed
    assert "CREATE INDEX ON Object(objectTypeApiName)" in executed
    assert "CREATE REL TABLE works_for (FROM Object TO Object" in executed

    # Metrics should exist and not raise
    assert metrics is not None
