from fastapi.testclient import TestClient


def _create_object_type(client: TestClient, api_name: str, pk: str, extra_props: dict):
    props = {
        pk: {"dataType": "string", "displayName": pk.upper(), "required": True},
    }
    props.update(extra_props)
    resp = client.put(
        f"/v2/ontologies/default/objectTypes/{api_name}",
        json={
            "displayName": api_name.title(),
            "primaryKey": pk,
            "properties": props,
        },
    )
    assert resp.status_code == 200, resp.text


def test_put_object_missing_required_property_returns_400(client: TestClient):
    _create_object_type(
        client,
        api_name="user",
        pk="id",
        extra_props={
            "email": {"dataType": "string", "displayName": "Email", "required": True},
            "name": {"dataType": "string", "displayName": "Name", "required": False},
        },
    )

    # Missing required 'email'
    resp = client.put(
        "/v2/ontologies/default/objects/user/1",
        json={"properties": {"name": "Alice"}},
    )
    assert resp.status_code == 400
    assert "Missing required properties" in resp.json()["detail"]


def test_put_object_unknown_property_returns_400(client: TestClient):
    _create_object_type(
        client,
        api_name="device",
        pk="id",
        extra_props={
            "model": {"dataType": "string", "displayName": "Model", "required": False},
        },
    )

    # Contains unknown property 'unknownField'
    resp = client.put(
        "/v2/ontologies/default/objects/device/XYZ",
        json={"properties": {"unknownField": "value"}},
    )
    assert resp.status_code == 400
    assert "Unknown properties" in resp.json()["detail"]


def test_put_object_type_mismatch_returns_400(client: TestClient):
    _create_object_type(
        client,
        api_name="person2",
        pk="id",
        extra_props={
            "age": {"dataType": "integer", "displayName": "Age", "required": False},
            "active": {"dataType": "boolean", "displayName": "Active", "required": False},
        },
    )

    # age expects integer, provide non-numeric string
    resp1 = client.put(
        "/v2/ontologies/default/objects/person2/1",
        json={"properties": {"age": "abc"}},
    )
    assert resp1.status_code == 400
    assert "Invalid value" in resp1.json()["detail"]

    # active expects boolean, provide unsupported string
    resp2 = client.put(
        "/v2/ontologies/default/objects/person2/1",
        json={"properties": {"active": "maybe"}},
    )
    assert resp2.status_code == 400
    assert "Invalid value" in resp2.json()["detail"]
