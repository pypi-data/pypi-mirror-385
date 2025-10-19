from fastapi.testclient import TestClient


def _put_person_ot(client: TestClient):
    r = client.put(
        "/v2/ontologies/default/objectTypes/person",
        json={
            "displayName": "Person",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "birthYear": {"dataType": "integer", "displayName": "Birth Year"},
                # age is derived: 2050 - birthYear
                "age": {
                    "dataType": "integer",
                    "displayName": "Age",
                    "derivationScript": "2050 - props['birthYear']",
                },
            },
        },
    )
    assert r.status_code == 200, r.text


def test_derived_property_is_computed_on_get(client: TestClient):
    _put_person_ot(client)

    # Upsert instance without the derived property
    r = client.put(
        "/v2/ontologies/default/objects/person/p1",
        json={"properties": {"id": "p1", "birthYear": 2000}},
    )
    assert r.status_code == 200, r.text

    # Read instance: derived age should be present and equal to 50
    r2 = client.get("/v2/ontologies/default/objects/person/p1")
    assert r2.status_code == 200, r2.text
    props = r2.json()["properties"]
    assert props.get("age") == 50
