from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.handlers.instances import get_instance_query_service
from api.main import app
from api.services.instances_service import ObjectInstanceQueryService
from api.v2.schemas.instances import ObjectReadResponse


class _FakeRepo:
    def __init__(self, objects: dict[str, dict[str, Any]]) -> None:
        self._objects = objects

    def get_object_instance(self, service: str, instance: str, object_type_api_name: str, pk: str):
        data = self._objects.get(pk)
        if not data:
            return None
        mock = MagicMock()
        mock.object_type_api_name = object_type_api_name
        mock.primary_key_field = "id"
        mock.data = data
        mock.rid = f"{object_type_api_name}:{pk}"
        mock.pk_value = pk
        return mock

    def list_object_instances(
        self,
        service: str,
        instance: str,
        *,
        object_type_api_name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        for pk, data in self._objects.items():
            mock = MagicMock()
            mock.object_type_api_name = object_type_api_name or "customer"
            mock.primary_key_field = "id"
            mock.data = data
            mock.rid = f"{mock.object_type_api_name}:{pk}"
            mock.pk_value = pk
            yield mock


class _FakeMetamodel:
    def get_object_type_by_api_name(self, service: str, instance: str, api_name: str):
        return MagicMock(primary_key_field="id")

    def get_interface_type_by_api_name(self, service: str, instance: str, api_name: str):
        raise Exception


class _FakeChangeSet:
    def __init__(self, payload: dict[str, Any], target: str = "customer") -> None:
        self.payload = payload
        self.service = "ontology"
        self.instance = "default"
        self.target_object_type = target


def _query_service(session, overlay_payload: dict[str, Any]) -> ObjectInstanceQueryService:
    session.get = MagicMock(return_value=_FakeChangeSet(overlay_payload))
    repo = _FakeRepo(
        {
            "c1": {"id": "c1", "name": "Alice"},
        }
    )
    svc = ObjectInstanceQueryService(
        session=session,
        service="ontology",
        instance="default",
        repo=repo,
        metamodel_repo=_FakeMetamodel(),
        graph_repo=None,
        kuzu_repo=None,
        principal=None,
        event_bus=MagicMock(),
    )
    return svc


def test_get_object_overlay_update(session):
    svc = _query_service(
        session,
        {"changes": [{"op": "update", "pk": "c1", "properties": {"name": "Bob"}}]},
    )
    result = svc.get_object("customer", "c1", change_set_rid="rid-1")
    assert result is not None
    assert result.properties["name"] == "Bob"


def test_get_object_overlay_delete(session):
    svc = _query_service(
        session,
        {"changes": [{"op": "delete", "pk": "c1"}]},
    )
    result = svc.get_object("customer", "c1", change_set_rid="rid-1")
    assert result is None


def test_list_objects_overlay_create(session):
    svc = _query_service(
        session,
        {
            "changes": [
                {"op": "create", "pk": "c2", "properties": {"id": "c2", "name": "Eve"}},
                {"op": "update", "pk": "c1", "properties": {"name": "Bob"}},
            ]
        },
    )
    results = svc.list_objects(change_set_rid="rid-1")
    names = {row.properties["name"] for row in results.data}
    assert names == {"Bob", "Eve"}


def test_api_header_overlay_session(session, client: TestClient):
    dummy_response = ObjectReadResponse(
        rid="customer:c1",
        objectTypeApiName="customer",
        pkValue="c1",
        properties={"id": "c1", "name": "Alice"},
    )

    query = MagicMock()
    query.get_object.return_value = dummy_response

    app.dependency_overrides[get_instance_query_service] = lambda: query
    try:
        resp = client.get(
            "/v2/ontologies/default/objects/customer/c1",
            headers={"X-Ontologia-ChangeSet-Rid": "rid-xyz"},
        )
    finally:
        app.dependency_overrides.pop(get_instance_query_service, None)

    assert resp.status_code == 200, resp.text
    query.get_object.assert_called_once()
    _, kwargs = query.get_object.call_args
    assert kwargs.get("change_set_rid") == "rid-xyz"
