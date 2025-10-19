from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlmodel import Session

from datacatalog.models import Dataset
from ontologia.application.sync_service import OntologySyncService


def _put_object_type(client: TestClient, api_name: str):
    resp = client.put(
        f"/v2/ontologies/default/objectTypes/{api_name}",
        json={
            "displayName": api_name.title(),
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
            },
        },
    )
    assert resp.status_code == 200, resp.text


def _put_link_type_with_backing(
    client: TestClient,
    link_api: str,
    from_ot: str,
    to_ot: str,
    backing_ds_api: str,
    from_col: str,
    to_col: str,
):
    resp = client.put(
        f"/v2/ontologies/default/linkTypes/{link_api}",
        json={
            "displayName": link_api.replace("_", " ").title(),
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": from_ot,
            "toObjectType": to_ot,
            "inverse": {"apiName": f"{link_api}_inv", "displayName": "Inverse"},
            "backingDatasetApiName": backing_ds_api,
            "fromPropertyMapping": from_col,
            "toPropertyMapping": to_col,
            "propertyMappings": {"weight": "w"},
        },
    )
    assert resp.status_code == 200, resp.text


class _DuckRes:
    def fetchone(self):
        return [2]


class _Duck:
    def execute(self, q: str):  # duckdb-like
        return _DuckRes()


def test_sync_rels_copy_path_executes_copy_and_counts(
    client: TestClient, session: Session, monkeypatch
):
    monkeypatch.setenv("SYNC_ENABLE_COPY_RELS", "1")

    # Arrange: object types
    _put_object_type(client, "employee")
    _put_object_type(client, "company")

    # Dataset for relations (duckdb table)
    ds = Dataset(
        service="ontology",
        instance="default",
        api_name="works_for_rels_ds",
        display_name="works_for_rels_ds",
        source_type="duckdb_table",
        source_identifier="works_for_rels_tbl",
        schema_definition={},
    )
    session.add(ds)
    session.commit()
    session.refresh(ds)

    # LinkType with backing dataset + mappings
    _put_link_type_with_backing(
        client,
        link_api="works_for",
        from_ot="employee",
        to_ot="company",
        backing_ds_api=ds.api_name,
        from_col="from_id",
        to_col="to_id",
    )

    # Prepare service with kuzu mock and duckdb stub
    mock_kuzu = MagicMock()
    svc = OntologySyncService(metadata_session=session, kuzu_conn=mock_kuzu, duckdb_conn=_Duck())

    # Act
    svc.sync_ontology()

    # Assert COPY called with expected parts
    executed = [str(call.args[0]) for call in mock_kuzu.execute.call_args_list]
    copy_calls = [q for q in executed if q.strip().startswith("COPY ")]
    assert any(
        ("COPY works_for FROM duckdb.works_for_rels_tbl" in q) and ("FROM from_id TO to_id" in q)
        for q in copy_calls
    ), executed

    # Assert metrics registered (row count mocked as 2)
    assert svc.metrics.rels_created.get("works_for", 0) == 2
