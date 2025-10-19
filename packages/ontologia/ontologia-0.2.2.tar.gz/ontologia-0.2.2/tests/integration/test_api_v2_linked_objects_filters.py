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
    assert (
        client.put(
            "/v2/ontologies/default/objects/employee/e1", json={"properties": {}}
        ).status_code
        == 200
    )
    assert (
        client.put(
            "/v2/ontologies/default/objects/employee/e2", json={"properties": {}}
        ).status_code
        == 200
    )
    assert (
        client.put("/v2/ontologies/default/objects/company/c1", json={"properties": {}}).status_code
        == 200
    )


def test_list_links_with_filters(client: TestClient):
    _setup_types_and_instances(client)

    # Create links: e1->c1 and e2->c1
    assert (
        client.post(
            "/v2/ontologies/default/links/works_for",
            json={"fromPk": "e1", "toPk": "c1"},
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/v2/ontologies/default/links/works_for",
            json={"fromPk": "e2", "toPk": "c1"},
        ).status_code
        == 201
    )

    # No filter -> 2
    res_all = client.get("/v2/ontologies/default/links/works_for")
    assert res_all.status_code == 200
    assert len(res_all.json()["data"]) == 2

    # Filter by fromPk
    res_from = client.get("/v2/ontologies/default/links/works_for", params={"fromPk": "e1"})
    assert res_from.status_code == 200
    body_from = res_from.json()
    assert len(body_from["data"]) == 1
    assert body_from["data"][0]["fromPk"] == "e1"
    assert body_from["data"][0]["toPk"] == "c1"

    # Filter by toPk
    res_to = client.get("/v2/ontologies/default/links/works_for", params={"toPk": "c1"})
    assert res_to.status_code == 200
    assert len(res_to.json()["data"]) == 2

    # Filter by non-existing
    res_none = client.get("/v2/ontologies/default/links/works_for", params={"fromPk": "e3"})
    assert res_none.status_code == 200
    assert len(res_none.json()["data"]) == 0
