from fastapi.testclient import TestClient


def ensure_object_types(client: TestClient):
    # employee
    resp1 = client.put(
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
    assert resp1.status_code == 200

    # company
    resp2 = client.put(
        "/v2/ontologies/default/objectTypes/company",
        json={
            "displayName": "Company",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
        },
    )
    assert resp2.status_code == 200


def test_link_type_create_and_update(client: TestClient):
    ensure_object_types(client)

    # Create link type works_for
    create = client.put(
        "/v2/ontologies/default/linkTypes/works_for",
        json={
            "displayName": "Works For",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employees"},
            "description": None,
        },
    )
    assert create.status_code == 200
    data = create.json()
    assert data["apiName"] == "works_for"
    assert data["cardinality"] == "MANY_TO_ONE"
    assert data["fromObjectType"] == "employee"
    assert data["toObjectType"] == "company"
    assert data["inverse"]["apiName"] == "has_employees"
    assert data["version"] == 1
    assert data["isLatest"] is True

    # Update: change cardinality and inverse display name
    update = client.put(
        "/v2/ontologies/default/linkTypes/works_for",
        json={
            "displayName": "Works For",
            "cardinality": "ONE_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employee"},
            "description": None,
        },
    )
    assert update.status_code == 200
    upd = update.json()
    assert upd["cardinality"] == "ONE_TO_ONE"
    assert upd["inverse"]["displayName"] == "Has Employee"
    assert upd["version"] == 2
    assert upd["isLatest"] is True

    # List should show exactly one link type
    lst = client.get("/v2/ontologies/default/linkTypes")
    assert lst.status_code == 200
    items = lst.json()["data"]
    assert len(items) == 1
    assert items[0]["apiName"] == "works_for"
    assert items[0]["version"] == 2
