from fastapi.testclient import TestClient


class _StubGraphRepo:
    def __init__(self, *args, **kwargs):
        pass

    def is_available(self) -> bool:
        return True

    def get_linked_objects(
        self,
        *,
        from_label: str,
        from_pk_field: str,
        from_pk_value: str,
        link_label: str,
        to_label: str,
        direction: str = "forward",
        limit: int = 100,
        offset: int = 0,
    ):
        # Simulate a single edge from employee(e1) -> department(d1)
        if from_label == "employee" and link_label == "works_in" and to_label == "department":
            return [
                {
                    "objectTypeApiName": "department",
                    "properties": {"id": "d1", "name": "Engineering"},
                }
            ][offset : offset + limit]
        return []


def _put_ot(client: TestClient, api: str):
    return client.put(
        f"/v2/ontologies/default/objectTypes/{api}",
        json={
            "displayName": api.title(),
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
        },
    )


def test_unified_traversal_uses_object_nodes(monkeypatch, client: TestClient):
    # Enable unified graph model
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")

    # Patch InstancesService to use our stubbed GraphInstancesRepository
    import api.services.instances_service as instances_service

    monkeypatch.setattr(instances_service, "GraphInstancesRepository", _StubGraphRepo)

    # Define object types and link type
    _put_ot(client, "employee")
    _put_ot(client, "department")

    # Create link type employee -> department
    rlt = client.put(
        "/v2/ontologies/default/linkTypes/works_in",
        json={
            "displayName": "Works In",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "department",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employees"},
        },
    )
    assert rlt.status_code == 200, rlt.text

    # Seed instances (not used by stub, but keeps consistent)
    client.put("/v2/ontologies/default/objects/employee/e1", json={"properties": {"name": "Alice"}})
    client.put(
        "/v2/ontologies/default/objects/department/d1", json={"properties": {"name": "Engineering"}}
    )

    # Traverse
    resp = client.get("/v2/ontologies/default/objects/employee/e1/works_in")
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["objectTypeApiName"] == "department"
    assert data[0]["pkValue"] == "d1"
    assert data[0]["properties"]["name"] == "Engineering"


def test_search_with_traverse_returns_target_objects(client: TestClient):
    _put_ot(client, "employee")
    _put_ot(client, "department")

    client.put(
        "/v2/ontologies/default/linkTypes/works_in",
        json={
            "displayName": "Works In",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "department",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employees"},
        },
    )

    client.put(
        "/v2/ontologies/default/objects/employee/e1",
        json={"properties": {"name": "Alice"}},
    )
    client.put(
        "/v2/ontologies/default/objects/department/d1",
        json={"properties": {"name": "Engineering"}},
    )

    client.post(
        "/v2/ontologies/default/links/works_in",
        json={"fromPk": "e1", "toPk": "d1", "properties": {}},
    )

    resp = client.post(
        "/v2/ontologies/default/objects/employee/search",
        json={
            "where": [{"property": "name", "op": "eq", "value": "Alice"}],
            "traverse": [
                {
                    "link": "works_in",
                    "where": [{"property": "name", "op": "eq", "value": "Engineering"}],
                }
            ],
        },
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()["data"]
    assert len(payload) == 1
    obj = payload[0]
    assert obj["objectTypeApiName"] == "department"
    assert obj["pkValue"] == "d1"
