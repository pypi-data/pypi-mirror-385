from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlmodel import select

from datacatalog.models import Dataset
from ontologia.application.sync_service import OntologySyncService
from ontologia.domain.metamodels.types.link_type import LinkType


def _create_basic_types(client: TestClient):
    # Create two OTs
    for name in ("src", "dst"):
        resp = client.put(
            f"/v2/ontologies/default/objectTypes/{name}",
            json={
                "displayName": name.title(),
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                },
            },
        )
        assert resp.status_code == 200, resp.text

    # Create link
    resp_link = client.put(
        "/v2/ontologies/default/linkTypes/relates",
        json={
            "displayName": "Relates",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "src",
            "toObjectType": "dst",
            "inverse": {"apiName": "related_by", "displayName": "Related By"},
        },
    )
    assert resp_link.status_code == 200, resp_link.text


def test_load_rels_uses_linktype_backing_dataset_and_mappings(client: TestClient, session):
    _create_basic_types(client)

    # Fetch link and create a dataset
    lt = session.exec(select(LinkType).where(LinkType.api_name == "relates")).one()

    ds = Dataset(
        service="ontology",
        instance="default",
        api_name="relates_ds",
        display_name="Relates DS",
        source_type="duckdb_table",
        source_identifier="relates_table",
        schema_definition={},
    )
    session.add(ds)
    session.commit()
    session.refresh(ds)

    # Configure LinkType mappings and backing dataset
    lt.backing_dataset_rid = ds.rid
    lt.from_property_mapping = "src_id"
    lt.to_property_mapping = "dst_id"
    lt.property_mappings = {"weight": "weight_col"}
    session.add(lt)
    session.commit()

    # Prepare service
    mock_kuzu = MagicMock()
    svc = OntologySyncService(metadata_session=session, kuzu_conn=mock_kuzu, duckdb_conn=None)

    # Monkeypatch read_dataset to return non-None
    old_read = OntologySyncService._read_dataset
    OntologySyncService._read_dataset = lambda _self, _ds: object()

    try:
        svc.sync_ontology()
    finally:
        OntologySyncService._read_dataset = old_read

    # Assert execute called with our mapped columns and dataset name
    cmds = [str(call.args[0]) for call in mock_kuzu.execute.call_args_list]
    match = [
        c
        for c in cmds
        if "relates" in c and "from_col=src_id" in c and "to_col=dst_id" in c and "relates_ds" in c
    ]
    assert match, f"Expected command with mapped cols; got: {cmds}"
