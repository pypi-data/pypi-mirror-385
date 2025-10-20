from fastapi.testclient import TestClient

from api.services.instances_service import InstancesService


class FakeGraphInstancesRepo:
    def is_available(self) -> bool:
        return True

    def get_by_pk(self, object_type_api_name: str, pk_field: str, pk_value: str):
        return {
            "objectTypeApiName": object_type_api_name,
            "pkValue": pk_value,
            "properties": {pk_field: pk_value, "name": "Alice"},
        }

    def list_by_type(self, object_type_api_name: str, *, limit: int = 100, offset: int = 0):
        return [
            {"properties": {"id": "e1", "name": "Alice"}},
            {"properties": {"id": "e2", "name": "Bob"}},
        ]


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
    assert resp.status_code == 200, resp.text


def test_graph_reads_get_and_list(client: TestClient, session, monkeypatch):
    # Enable graph reads
    monkeypatch.setenv("USE_GRAPH_READS", "1")

    _create_employee_object_type(client)

    svc = InstancesService(
        session, service="ontology", instance="default", graph_repo=FakeGraphInstancesRepo()
    )

    # get_object via graph
    got = svc.get_object("employee", "e1")
    assert got is not None
    assert got.objectTypeApiName == "employee"
    assert got.pkValue == "e1"
    assert got.properties.get("name") == "Alice"

    # list_objects via graph
    lst = svc.list_objects(object_type_api_name="employee")
    assert len(lst.data) == 2
    pks = sorted([it.pkValue for it in lst.data])
    assert pks == ["e1", "e2"]
