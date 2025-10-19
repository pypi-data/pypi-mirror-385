from fastapi.testclient import TestClient


def _setup_basic_types(client: TestClient):
    # Create ObjectTypes: employee, company
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


def _create_instance(client: TestClient, ot: str, pk: str):
    resp = client.put(f"/v2/ontologies/default/objects/{ot}/{pk}", json={"properties": {}})
    assert resp.status_code == 200, resp.text


def _create_link(client: TestClient, link_type: str, from_pk: str, to_pk: str):
    resp = client.post(
        f"/v2/ontologies/default/links/{link_type}", json={"fromPk": from_pk, "toPk": to_pk}
    )
    assert resp.status_code == 201, resp.text


def test_traversal_forward_sql_fallback(client: TestClient):
    _setup_basic_types(client)
    _create_instance(client, "employee", "e1")
    _create_instance(client, "company", "c1")
    _create_link(client, "works_for", "e1", "c1")

    # Traverse forward: employee e1 -> company
    resp = client.get("/v2/ontologies/default/objects/employee/e1/works_for")
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["objectTypeApiName"] == "company"
    assert data[0]["pkValue"] == "c1"


def test_traversal_inverse_with_pagination_sql_fallback(client: TestClient):
    _setup_basic_types(client)
    # company c1 with two employees
    _create_instance(client, "company", "c1")
    for e in ("e1", "e2"):
        _create_instance(client, "employee", e)
        _create_link(client, "works_for", e, "c1")

    # Full traversal inverse: company c1 <- employees
    full = client.get("/v2/ontologies/default/objects/company/c1/works_for")
    assert full.status_code == 200, full.text
    full_pks = {item["pkValue"] for item in full.json()["data"]}
    assert full_pks == {"e1", "e2"}

    # Paginated: limit=1
    p1 = client.get("/v2/ontologies/default/objects/company/c1/works_for?limit=1")
    assert p1.status_code == 200
    d1 = p1.json()["data"]
    assert len(d1) == 1

    # Paginated: limit=1, offset=1
    p2 = client.get("/v2/ontologies/default/objects/company/c1/works_for?limit=1&offset=1")
    assert p2.status_code == 200
    d2 = p2.json()["data"]
    assert len(d2) == 1

    # Union of paginated results should equal the full set
    union = {d1[0]["pkValue"], d2[0]["pkValue"]}
    assert union == full_pks
