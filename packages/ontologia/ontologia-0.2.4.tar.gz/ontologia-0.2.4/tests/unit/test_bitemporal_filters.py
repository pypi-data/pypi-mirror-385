from datetime import datetime

from fastapi.testclient import TestClient

from api.services.instances_service import InstancesService
from api.services.linked_objects_service import LinkedObjectsService
from api.v2.schemas.instances import ObjectUpsertRequest
from api.v2.schemas.linked_objects import LinkCreateRequest


def _setup_contract_type(client: TestClient) -> None:
    resp = client.put(
        "/v2/ontologies/default/objectTypes/contract",
        json={
            "displayName": "Contract",
            "primaryKey": "id",
            "properties": {
                "id": {
                    "dataType": "string",
                    "displayName": "ID",
                    "required": True,
                },
                "valid_from": {
                    "dataType": "timestamp",
                    "displayName": "Valid From",
                },
                "valid_to": {
                    "dataType": "timestamp",
                    "displayName": "Valid To",
                },
            },
        },
    )
    assert resp.status_code == 200, resp.text


def _setup_party_type(client: TestClient) -> None:
    resp = client.put(
        "/v2/ontologies/default/objectTypes/party",
        json={
            "displayName": "Party",
            "primaryKey": "id",
            "properties": {
                "id": {
                    "dataType": "string",
                    "displayName": "ID",
                    "required": True,
                }
            },
        },
    )
    assert resp.status_code == 200, resp.text


def _setup_contract_party_link(client: TestClient) -> None:
    resp = client.put(
        "/v2/ontologies/default/linkTypes/party_to_contract",
        json={
            "displayName": "Party to Contract",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "party",
            "toObjectType": "contract",
            "inverse": {
                "apiName": "contract_has_party",
                "displayName": "Contract Has Party",
            },
            "properties": {
                "valid_from": {
                    "dataType": "timestamp",
                    "displayName": "Valid From",
                },
                "valid_to": {
                    "dataType": "timestamp",
                    "displayName": "Valid To",
                },
            },
        },
    )
    assert resp.status_code == 200, resp.text


def test_list_objects_validity_filter(client: TestClient, session) -> None:
    _setup_contract_type(client)

    svc = InstancesService(session, service="ontology", instance="default")
    svc.upsert_object(
        "contract",
        "c1",
        ObjectUpsertRequest(
            properties={
                "id": "c1",
                "valid_from": "2023-01-01T00:00:00",
                "valid_to": "2023-06-01T00:00:00",
            }
        ),
    )

    # No filter -> present
    assert len(svc.list_objects("contract").data) == 1

    # Before validity
    past = datetime.fromisoformat("2022-12-01T00:00:00")
    assert len(svc.list_objects("contract", valid_at=past).data) == 0

    # During validity
    mid = datetime.fromisoformat("2023-03-01T00:00:00")
    data_mid = svc.list_objects("contract", valid_at=mid).data
    assert len(data_mid) == 1
    assert data_mid[0].pkValue == "c1"

    # After validity (exclusive upper bound)
    future = datetime.fromisoformat("2023-07-01T00:00:00")
    assert len(svc.list_objects("contract", valid_at=future).data) == 0


def test_link_validity_filter(client: TestClient, session) -> None:
    _setup_party_type(client)
    _setup_contract_type(client)
    _setup_contract_party_link(client)

    inst = InstancesService(session, service="ontology", instance="default")
    inst.upsert_object("party", "p1", ObjectUpsertRequest(properties={"id": "p1"}))
    inst.upsert_object(
        "contract",
        "c1",
        ObjectUpsertRequest(
            properties={
                "id": "c1",
                "valid_from": "2023-01-01T00:00:00",
                "valid_to": "2023-12-31T00:00:00",
            }
        ),
    )

    links = LinkedObjectsService(session, service="ontology", instance="default")
    links.create_link(
        "party_to_contract",
        LinkCreateRequest(
            fromPk="p1",
            toPk="c1",
            properties={
                "valid_from": "2023-01-01T00:00:00",
                "valid_to": "2023-04-01T00:00:00",
            },
        ),
    )

    mid = datetime.fromisoformat("2023-02-01T00:00:00")
    data_mid = links.list_links("party_to_contract", valid_at=mid).data
    assert len(data_mid) == 1

    late = datetime.fromisoformat("2023-05-01T00:00:00")
    assert len(links.list_links("party_to_contract", valid_at=late).data) == 0
