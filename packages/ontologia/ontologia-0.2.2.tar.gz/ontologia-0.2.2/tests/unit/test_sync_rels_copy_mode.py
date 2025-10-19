from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlmodel import select

from datacatalog.models import Dataset
from ontologia.application.sync_service import OntologySyncService
from ontologia.domain.metamodels.types.link_type import LinkType


def _ensure_employee_company_and_link(client: TestClient):
    # Create employee and company OTs
    for name in ("employee", "company"):
        props = {
            "id": {"dataType": "string", "displayName": "ID", "required": True},
        }
        if name == "employee":
            props["name"] = {"dataType": "string", "displayName": "Name", "required": False}
        resp = client.put(
            f"/v2/ontologies/default/objectTypes/{name}",
            json={
                "displayName": name.title(),
                "primaryKey": "id",
                "properties": props,
            },
        )
        assert resp.status_code == 200, resp.text

    # Create link works_for
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
    assert resp_link.status_code == 200, resp_link.text


def test_sync_rels_copy_mode_uses_copy_command(monkeypatch, client: TestClient, session):
    _ensure_employee_company_and_link(client)

    # Create join dataset
    ds = Dataset(
        service="ontology",
        instance="default",
        api_name="works_for_ds",
        display_name="Works For DS",
        source_type="duckdb_table",
        source_identifier="works_for_tbl",
        schema_definition={},
    )
    session.add(ds)
    session.commit()
    session.refresh(ds)

    # Configure LinkType to use dataset and mappings
    lt = session.exec(select(LinkType).where(LinkType.api_name == "works_for")).one()
    lt.backing_dataset_rid = ds.rid
    lt.from_property_mapping = "emp_id"
    lt.to_property_mapping = "company_id"
    session.add(lt)
    session.commit()

    # Enable COPY mode
    monkeypatch.setenv("SYNC_ENABLE_COPY_RELS", "1")

    mock_kuzu = MagicMock()
    svc = OntologySyncService(metadata_session=session, kuzu_conn=mock_kuzu, duckdb_conn=None)

    # Run sync with a duckdb_path to trigger ATTACH (no real kuzu/duckdb needed)
    svc.sync_ontology(duckdb_path=":memory:")

    # Assert COPY command was issued with the correct source and columns
    executed_cmds = [str(call.args[0]) for call in mock_kuzu.execute.call_args_list]
    matches = [
        c
        for c in executed_cmds
        if "COPY works_for FROM duckdb.works_for_tbl" in c and "FROM emp_id TO company_id" in c
    ]
    assert matches, f"Expected COPY works_for ... FROM emp_id TO company_id; got: {executed_cmds}"
