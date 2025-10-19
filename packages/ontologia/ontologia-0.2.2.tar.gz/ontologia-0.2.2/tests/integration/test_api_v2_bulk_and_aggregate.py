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
                "dept": {"dataType": "string", "displayName": "Dept", "required": False},
            },
        },
    )


def test_bulk_objects_and_links_and_aggregate(client: TestClient):
    _put_ot(client, "employee")
    _put_ot(client, "department")

    # Create link type employee -> department
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

    # Bulk load employees
    r = client.post(
        "/v2/ontologies/default/objects/employee/load",
        json={
            "items": [
                {"pk": "e1", "properties": {"age": 25, "dept": "ENG"}},
                {"pk": "e2", "properties": {"age": 35, "dept": "ENG"}},
                {"pk": "e3", "properties": {"age": 29, "dept": "HR"}},
            ]
        },
    )
    assert r.status_code == 200, r.text
    assert len(r.json()["data"]) == 3

    # Create departments
    client.put("/v2/ontologies/default/objects/department/d1", json={"properties": {}})
    client.put("/v2/ontologies/default/objects/department/d2", json={"properties": {}})

    # Bulk create links
    r2 = client.post(
        "/v2/ontologies/default/links/works_in/load",
        json={
            "mode": "create",
            "items": [
                {"fromPk": "e1", "toPk": "d1"},
                {"fromPk": "e2", "toPk": "d1"},
                {"fromPk": "e3", "toPk": "d2"},
            ],
        },
    )
    assert r2.status_code == 200, r2.text
    assert len(r2.json()["data"]) == 3

    # Aggregate: count employees by dept, and avg age
    a = client.post(
        "/v2/ontologies/default/aggregate",
        json={
            "objectTypeApiName": "employee",
            "where": [],
            "groupBy": ["dept"],
            "metrics": [{"func": "count"}, {"func": "avg", "property": "age"}],
        },
    )
    assert a.status_code == 200, a.text
    rows = a.json()["rows"]
    # Expect two groups: ENG and HR
    groups = {row["group"].get("dept"): row for row in rows}
    assert set(groups.keys()) == {"ENG", "HR"}
    assert groups["ENG"]["metrics"]["count"] == 2
    assert groups["HR"]["metrics"]["count"] == 1
