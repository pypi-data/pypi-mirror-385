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


def test_query_types_alias_query_and_target(client: TestClient):
    _put_ot(client, "customer")

    # Seed customers
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

    # Create a QueryType using SDK-parity aliases: targetApiName and unified query with {{param}}
    qt = client.put(
        "/v2/ontologies/default/queryTypes/adults_in_region_alias",
        json={
            "displayName": "Adults In Region Alias",
            "targetApiName": "customer",
            "parameters": {
                "minAge": {
                    "dataType": "integer",
                    "displayName": "Min Age",
                    "required": True,
                },
                "region": {
                    "dataType": "string",
                    "displayName": "Region",
                    "required": True,
                },
            },
            "query": {
                "where": [
                    {"property": "age", "op": "gte", "value": "{{minAge}}"},
                    {"property": "region", "op": "eq", "value": "{{region}}"},
                ],
                "orderBy": [{"property": "age", "direction": "asc"}],
            },
        },
    )
    assert qt.status_code == 200, qt.text
    qt_body = qt.json()
    assert qt_body["version"] == 1
    assert qt_body["isLatest"] is True

    # Execute with params: expect EU customers with age >= 30 => c2 and c3
    ex = client.post(
        "/v2/ontologies/default/queries/adults_in_region_alias/execute",
        json={"parameters": {"minAge": 30, "region": "EU"}},
    )
    assert ex.status_code == 200, ex.text
    data = ex.json()["data"]
    pks = {item["pkValue"] for item in data}
    assert pks == {"c2", "c3"}
