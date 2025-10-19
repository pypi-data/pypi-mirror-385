from fastapi.testclient import TestClient


def _put_ot(client: TestClient, api: str):
    return client.put(
        f"/v2/ontologies/default/objectTypes/{api}",
        json={
            "displayName": api.capitalize(),
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "age": {"dataType": "integer", "displayName": "Age", "required": False},
                "region": {"dataType": "string", "displayName": "Region", "required": False},
            },
        },
    )


def test_query_types_crud_and_execute(client: TestClient):
    # Define object type and seed data
    r = _put_ot(client, "customer")
    assert r.status_code == 200, r.text

    # Upsert some customers
    client.put(
        "/v2/ontologies/default/objects/customer/c1",
        json={"properties": {"age": 18, "region": "NA"}},
    )
    client.put(
        "/v2/ontologies/default/objects/customer/c2",
        json={"properties": {"age": 30, "region": "EU"}},
    )
    client.put(
        "/v2/ontologies/default/objects/customer/c3",
        json={"properties": {"age": 42, "region": "EU"}},
    )

    # Create a QueryType: adults in region with parameterized minAge and region
    qt = client.put(
        "/v2/ontologies/default/queryTypes/adults_in_region",
        json={
            "displayName": "Adults In Region",
            "targetObjectType": "customer",
            "parameters": {
                "minAge": {"dataType": "integer", "displayName": "Min Age", "required": True},
                "region": {"dataType": "string", "displayName": "Region", "required": True},
            },
            "whereTemplate": [
                {"property": "age", "op": "gte", "value": {"param": "minAge"}},
                {"property": "region", "op": "eq", "value": {"param": "region"}},
            ],
            "orderByTemplate": [{"property": "age", "direction": "asc"}],
        },
    )
    assert qt.status_code == 200, qt.text
    qt_body = qt.json()
    assert qt_body["apiName"] == "adults_in_region"
    assert qt_body["version"] == 1
    assert qt_body["isLatest"] is True

    # List and get
    lst = client.get("/v2/ontologies/default/queryTypes")
    assert lst.status_code == 200
    assert any(
        item["apiName"] == "adults_in_region" and item["version"] == 1
        for item in lst.json()["data"]
    )

    getr = client.get("/v2/ontologies/default/queryTypes/adults_in_region")
    assert getr.status_code == 200

    # Execute with params: expect EU customers with age >= 30 => c2 and c3
    ex = client.post(
        "/v2/ontologies/default/queries/adults_in_region/execute",
        json={"parameters": {"minAge": 30, "region": "EU"}},
    )
    assert ex.status_code == 200, ex.text
    data = ex.json()["data"]
    pks = {item["pkValue"] for item in data}
    assert pks == {"c2", "c3"}

    # Delete
    d = client.delete("/v2/ontologies/default/queryTypes/adults_in_region")
    assert d.status_code == 204
