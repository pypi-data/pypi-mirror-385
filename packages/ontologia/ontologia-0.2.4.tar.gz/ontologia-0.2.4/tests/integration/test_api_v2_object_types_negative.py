from fastapi.testclient import TestClient


def test_put_object_type_missing_pk_returns_400(client: TestClient):
    payload = {
        "displayName": "Product",
        "primaryKey": "id",
        "properties": {
            # 'id' intentionally missing
            "name": {"dataType": "string", "displayName": "Name", "required": False}
        },
    }
    resp = client.put("/v2/ontologies/default/objectTypes/Product", json=payload)
    assert resp.status_code == 400
    assert "must be defined in properties" in resp.json()["detail"]


def test_put_object_type_pk_not_required_returns_400(client: TestClient):
    payload = {
        "displayName": "Product",
        "primaryKey": "id",
        "properties": {"id": {"dataType": "string", "displayName": "ID", "required": False}},
    }
    resp = client.put("/v2/ontologies/default/objectTypes/Product", json=payload)
    assert resp.status_code == 400
    assert "must be required" in resp.json()["detail"]
