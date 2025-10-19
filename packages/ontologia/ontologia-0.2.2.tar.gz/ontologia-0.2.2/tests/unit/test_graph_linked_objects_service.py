from fastapi.testclient import TestClient

from api.services.linked_objects_service import LinkedObjectsService


class FakeGraphLinkedRepo:
    def is_available(self) -> bool:
        return True

    def list_edges(
        self,
        link_type_api_name: str,
        from_label: str,
        to_label: str,
        from_pk_field: str,
        to_pk_field: str,
        *,
        limit: int = 100,
        offset: int = 0,
        property_names: list[str] | None = None,
    ):
        return [
            {"fromPk": "e1", "toPk": "c1"},
            {"fromPk": "e2", "toPk": "c1"},
        ]


def _setup_types_and_link(client: TestClient):
    # Create OTs
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

    # Create LinkType MANY_TO_ONE: employee -> company
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


def test_graph_reads_list_links(client: TestClient, session, monkeypatch):
    # Enable graph reads
    monkeypatch.setenv("USE_GRAPH_READS", "1")

    _setup_types_and_link(client)

    svc = LinkedObjectsService(
        session,
        service="ontology",
        instance="default",
        graph_repo=FakeGraphLinkedRepo(),
    )

    # list_links via graph (no data in SQLModel needed)
    lst = svc.list_links("works_for")
    assert len(lst.data) == 2
    pairs = {(it.fromPk, it.toPk) for it in lst.data}
    assert pairs == {("e1", "c1"), ("e2", "c1")}
