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


def _setup_types_with_link_props(client: TestClient):
    # Create employee and company object types via API
    for ot_name in ("employee", "company"):
        resp = client.put(
            f"/v2/ontologies/default/objectTypes/{ot_name}",
            json={
                "displayName": ot_name.title(),
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                },
            },
        )
        assert resp.status_code == 200, resp.text

    # Create LinkType with link properties
    resp_link = client.put(
        "/v2/ontologies/default/linkTypes/works_for",
        json={
            "displayName": "Works For",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employees"},
            "properties": {
                "sinceDate": {"dataType": "string", "displayName": "Since"},
                "role": {"dataType": "string", "displayName": "Role"},
            },
        },
    )
    assert resp_link.status_code == 200, resp_link.text


def test_graph_writes_link_with_properties(client: TestClient, session, monkeypatch):
    _setup_types_with_link_props(client)

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

    inst_svc.upsert_object("employee", "e1", ObjectUpsertRequest(properties={}))
    inst_svc.upsert_object("company", "c1", ObjectUpsertRequest(properties={}))

    fake.commands.clear()

    link_svc = LinkedObjectsService(
        session,
        service="ontology",
        instance="default",
        event_bus=bus,
    )
    resp = link_svc.create_link(
        "works_for",
        LinkCreateRequest(
            fromPk="e1", toPk="c1", properties={"sinceDate": "2021-06-01", "role": "Engineer"}
        ),
    )
    assert resp.linkTypeApiName == "works_for"

    joined = "\n".join(fake.commands)
    assert "MATCH (a:`employee`" in joined or "MATCH (a:employee" in joined
    assert "(b:`company`" in joined or "(b:company" in joined
    assert "CREATE (a)-[r:`works_for`]->(b)" in joined or "CREATE (a)-[r:works_for]->(b)" in joined
    assert "r.sinceDate = '2021-06-01'" in joined
    assert "r.role = 'Engineer'" in joined
