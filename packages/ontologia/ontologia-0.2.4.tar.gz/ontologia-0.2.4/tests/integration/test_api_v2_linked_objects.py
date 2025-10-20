from fastapi.testclient import TestClient


def _setup_types_and_instances(client: TestClient):
    # Create OTs
    for ot_name in ("employee", "company"):
        resp = client.put(
            f"/v2/ontologies/default/objectTypes/{ot_name}",
            json={
                "displayName": ot_name.title(),
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                },
            },
        )
        assert resp.status_code == 200, resp.text

    # Create LinkType MANY_TO_ONE: employee -> company
    resp_link = client.put(
        "/v2/ontologies/default/linkTypes/works_for",
        json={
            "displayName": "Works For",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employees"},
        },
    )
    assert resp_link.status_code == 200, resp_link.text

    # Create instances
    r1 = client.put("/v2/ontologies/default/objects/employee/e1", json={"properties": {}})
    r2 = client.put("/v2/ontologies/default/objects/company/c1", json={"properties": {}})
    assert r1.status_code == 200 and r2.status_code == 200


def test_create_list_delete_link(client: TestClient):
    _setup_types_and_instances(client)

    # Create link employee e1 -> company c1
    create = client.post(
        "/v2/ontologies/default/links/works_for",
        json={"fromPk": "e1", "toPk": "c1"},
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["linkTypeApiName"] == "works_for"
    assert body["fromPk"] == "e1"
    assert body["toPk"] == "c1"

    # List
    lst = client.get("/v2/ontologies/default/links/works_for")
    assert lst.status_code == 200
    assert len(lst.json()["data"]) == 1

    # Delete
    dele = client.delete("/v2/ontologies/default/links/works_for/e1/c1")
    assert dele.status_code == 204

    # List empties
    lst2 = client.get("/v2/ontologies/default/links/works_for")
    assert lst2.status_code == 200
    assert len(lst2.json()["data"]) == 0


def test_cardinality_enforced_forward_one(client: TestClient):
    _setup_types_and_instances(client)

    # Change link cardinality to ONE_TO_ONE to test forward one
    client.put(
        "/v2/ontologies/default/linkTypes/mentors",
        json={
            "displayName": "Mentors",
            "cardinality": "ONE_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "mentored_by", "displayName": "Mentored By"},
        },
    )
    # First ok
    ok = client.post(
        "/v2/ontologies/default/links/mentors",
        json={"fromPk": "e1", "toPk": "c1"},
    )
    assert ok.status_code == 201
    # Second should fail forward ONE
    bad = client.post(
        "/v2/ontologies/default/links/mentors",
        json={"fromPk": "e1", "toPk": "c1"},
    )
    assert bad.status_code == 400
    assert "Cardinality violation" in bad.json()["detail"]
