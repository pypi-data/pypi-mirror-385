from fastapi.testclient import TestClient


def _put_ot(client: TestClient, api: str):
    return client.put(
        f"/v2/ontologies/default/objectTypes/{api}",
        json={
            "displayName": api.capitalize(),
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "score": {"dataType": "double", "displayName": "Score", "required": False},
                "group": {"dataType": "string", "displayName": "Group", "required": False},
            },
        },
    )


def test_objects_nested_aggregate(client: TestClient):
    _put_ot(client, "item")

    # Seed items
    client.put(
        "/v2/ontologies/default/objects/item/a", json={"properties": {"score": 1.5, "group": "X"}}
    )
    client.put(
        "/v2/ontologies/default/objects/item/b", json={"properties": {"score": 2.5, "group": "X"}}
    )
    client.put(
        "/v2/ontologies/default/objects/item/c", json={"properties": {"score": 4.0, "group": "Y"}}
    )

    # Aggregate by group with avg(score)
    r = client.post(
        "/v2/ontologies/default/objects/item/aggregate",
        json={"where": [], "groupBy": ["group"], "metrics": [{"func": "avg", "property": "score"}]},
    )
    assert r.status_code == 200, r.text
    rows = r.json()["rows"]
    groups = {row["group"].get("group"): row for row in rows}
    assert set(groups.keys()) == {"X", "Y"}
    # avg for X should be 2.0 (1.5 and 2.5), for Y should be 4.0
    assert abs(groups["X"]["metrics"]["avg(score)"] - 2.0) < 1e-9
    assert abs(groups["Y"]["metrics"]["avg(score)"] - 4.0) < 1e-9
