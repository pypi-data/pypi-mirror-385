from fastapi.testclient import TestClient


def test_create_object_type_success(client: TestClient):
    resp = client.put(
        "/v2/ontologies/default/objectTypes/Funcionario",
        json={
            "displayName": "Funcionário",
            "description": None,
            "primaryKey": "employeeId",
            "properties": {
                "employeeId": {
                    "dataType": "string",
                    "displayName": "Employee ID",
                    "required": True,
                },
                "name": {
                    "dataType": "string",
                    "displayName": "Name",
                    "required": False,
                },
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["apiName"] == "Funcionario"
    assert data["primaryKey"] == "employeeId"
    assert data["version"] == 1
    assert data["isLatest"] is True
    assert "employeeId" in data["properties"]
    assert "name" in data["properties"]


def test_upsert_object_type_reconciliation(client: TestClient):
    # 1) Create initial type
    create = client.put(
        "/v2/ontologies/default/objectTypes/customer",
        json={
            "displayName": "Customer",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
        },
    )
    assert create.status_code == 200

    # 2) Update removing 'name' and adding 'email'
    update = client.put(
        "/v2/ontologies/default/objectTypes/customer",
        json={
            "displayName": "Customer",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "email": {"dataType": "string", "displayName": "Email", "required": False},
            },
        },
    )
    assert update.status_code == 200
    data = update.json()
    assert data["version"] == 2
    assert data["isLatest"] is True
    props = data["properties"]
    assert "id" in props
    assert "email" in props
    assert "name" not in props

    previous = client.get(
        "/v2/ontologies/default/objectTypes/customer",
        params={"version": 1},
    )
    assert previous.status_code == 200
    prev_data = previous.json()
    assert prev_data["version"] == 1
    assert prev_data["isLatest"] is False
    prev_props = prev_data["properties"]
    assert "id" in prev_props
    assert "name" in prev_props
    assert "email" not in prev_props

    historical = client.get(
        "/v2/ontologies/default/objectTypes",
        params={"includeHistorical": True},
    )
    assert historical.status_code == 200
    hist_data = historical.json()["data"]
    versions = {item["version"] for item in hist_data if item["apiName"] == "customer"}
    assert {1, 2}.issubset(versions)
