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
                "city": {"dataType": "string", "displayName": "City", "required": False},
            },
        },
    )


def _put_obj(client: TestClient, ot: str, pk: str, props: dict):
    p = dict(props or {})
    return client.put(f"/v2/ontologies/default/objects/{ot}/{pk}", json={"properties": p})


def test_search_basic_filters_and_ordering(client: TestClient):
    _put_ot(client, "person")
    _put_obj(client, "person", "p1", {"age": 25, "city": "São Paulo"})
    _put_obj(client, "person", "p2", {"age": 35, "city": "São Paulo"})
    _put_obj(client, "person", "p3", {"age": 40, "city": "Rio"})

    # age > 30 AND city == 'São Paulo', order by age desc
    r = client.post(
        "/v2/ontologies/default/objects/person/search",
        json={
            "where": [
                {"property": "city", "op": "eq", "value": "São Paulo"},
                {"property": "age", "op": "gt", "value": 30},
            ],
            "orderBy": [{"property": "age", "direction": "desc"}],
            "limit": 100,
            "offset": 0,
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert [d["pkValue"] for d in data] == ["p2"]


def test_search_contains_and_pagination(client: TestClient):
    _put_ot(client, "customer")
    _put_obj(client, "customer", "c1", {"city": "São Paulo"})
    _put_obj(client, "customer", "c2", {"city": "Santos"})
    _put_obj(client, "customer", "c3", {"city": "São Carlos"})

    # contains 'são' case-insensitive, order by city asc, paginate limit=1
    r1 = client.post(
        "/v2/ontologies/default/objects/customer/search",
        json={
            "where": [{"property": "city", "op": "contains", "value": "são"}],
            "orderBy": [{"property": "city", "direction": "asc"}],
            "limit": 1,
            "offset": 0,
        },
    )
    assert r1.status_code == 200, r1.text
    d1 = r1.json()["data"]
    assert len(d1) == 1

    r2 = client.post(
        "/v2/ontologies/default/objects/customer/search",
        json={
            "where": [{"property": "city", "op": "contains", "value": "são"}],
            "orderBy": [{"property": "city", "direction": "asc"}],
            "limit": 1,
            "offset": 1,
        },
    )
    assert r2.status_code == 200
    d2 = r2.json()["data"]
    assert len(d2) == 1

    # union of PKs equals the set of all matches of contains('são')
    allr = client.post(
        "/v2/ontologies/default/objects/customer/search",
        json={
            "where": [{"property": "city", "op": "contains", "value": "são"}],
            "orderBy": [{"property": "city", "direction": "asc"}],
            "limit": 10,
            "offset": 0,
        },
    )
    assert allr.status_code == 200
    allpks = [d["pkValue"] for d in allr.json()["data"]]
    assert set([d1[0]["pkValue"], d2[0]["pkValue"]]) <= set(allpks)
