from fastapi.testclient import TestClient

from api.event_handlers import register_graph_event_handlers
from api.services.instances_service import InstancesService
from api.v2.schemas.instances import ObjectUpsertRequest
from ontologia.domain.events import InProcessEventBus


class FakeKuzuRepo:
    def __init__(self):
        self.commands: list[str] = []

    def is_available(self) -> bool:
        return True

    def execute(self, query: str):
        # Record cypher queries for assertions
        self.commands.append(query)

        class _Res:
            def get_as_df(self):
                return None

        return _Res()


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


def test_graph_writes_instances_upsert_and_delete(client: TestClient, session, monkeypatch):
    monkeypatch.setenv("USE_GRAPH_WRITES", "1")
    fake = FakeKuzuRepo()
    import api.event_handlers.graph as graph_handlers

    monkeypatch.setattr(graph_handlers, "get_kuzu_repo", lambda: fake)
    bus = InProcessEventBus()
    register_graph_event_handlers(bus)

    _create_employee_object_type(client)

    svc = InstancesService(session, service="ontology", instance="default", event_bus=bus)

    # Upsert instance (should attempt MATCH/SET and CREATE)
    svc.upsert_object(
        "employee",
        "e1",
        body=ObjectUpsertRequest(properties={"name": "Alice"}),
    )

    joined = "\n".join(fake.commands)
    assert "MATCH (o:`employee`" in joined or "MATCH (o:employee" in joined
    assert "SET o.id = 'e1'" in joined or "SET o.name = 'Alice'" in joined
    assert "CREATE (:employee {" in joined

    # Delete instance (should issue DELETE)
    svc.delete_object("employee", "e1")
    joined2 = "\n".join(fake.commands)
    assert "DELETE o" in joined2
