from fastapi.testclient import TestClient

from api.event_handlers import register_graph_event_handlers
from api.services.instances_service import InstancesService
from api.services.linked_objects_service import LinkedObjectsService
from api.v2.schemas.instances import ObjectUpsertRequest
from api.v2.schemas.linked_objects import LinkCreateRequest
from ontologia.domain.events import InProcessEventBus


class FakeKuzuRepo:
    def __init__(self):
        self.commands: list[str] = []

    def is_available(self) -> bool:
        return True

    def execute(self, query: str):
        self.commands.append(query)

        class _Res:
            def get_as_df(self):
                return None

        return _Res()


def _setup_types(client: TestClient):
    # Create employee (with 'name') and company object types via API
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

    resp2 = client.put(
        "/v2/ontologies/default/objectTypes/company",
        json={
            "displayName": "Company",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
            },
        },
    )
    assert resp2.status_code == 200, resp2.text

    # Create LinkType MANY_TO_ONE employee -> company
    resp3 = client.put(
        "/v2/ontologies/default/linkTypes/works_for",
        json={
            "displayName": "Works For",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employees"},
        },
    )
    assert resp3.status_code == 200, resp3.text


def test_graph_writes_linked_objects_create_and_delete(client: TestClient, session, monkeypatch):
    _setup_types(client)

    monkeypatch.setenv("USE_GRAPH_WRITES", "1")
    fake = FakeKuzuRepo()
    import api.event_handlers.graph as graph_handlers

    monkeypatch.setattr(graph_handlers, "get_kuzu_repo", lambda: fake)
    bus = InProcessEventBus()
    register_graph_event_handlers(bus)

    inst_svc = InstancesService(
        session,
        service="ontology",
        instance="default",
        event_bus=bus,
    )

    inst_svc.upsert_object("employee", "e1", ObjectUpsertRequest(properties={"name": "Alice"}))
    inst_svc.upsert_object("company", "c1", ObjectUpsertRequest(properties={}))

    link_svc = LinkedObjectsService(
        session,
        service="ontology",
        instance="default",
        event_bus=bus,
    )

    fake.commands.clear()

    # Create link (should issue MATCH ... CREATE)
    resp = link_svc.create_link("works_for", LinkCreateRequest(fromPk="e1", toPk="c1"))
    assert resp.linkTypeApiName == "works_for"

    joined = "\n".join(fake.commands)
    assert "MATCH (a:`employee`" in joined or "MATCH (a:employee" in joined
    assert "(b:`company`" in joined or "(b:company" in joined
    assert "CREATE (a)-[r:`works_for`]->(b)" in joined or "CREATE (a)-[:works_for]->(b)" in joined

    # Delete link (should issue MATCH ... DELETE r)
    ok = link_svc.delete_link("works_for", "e1", "c1")
    assert ok is True
    joined2 = "\n".join(fake.commands)
    assert "DELETE r" in joined2
