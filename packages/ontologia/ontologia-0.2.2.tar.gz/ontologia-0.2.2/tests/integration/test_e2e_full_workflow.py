from __future__ import annotations

from fastapi.testclient import TestClient


def _put_employee_and_company(client: TestClient) -> None:
    for api_name, props in (
        (
            "employee",
            {
                "displayName": "Employee",
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                    "name": {"dataType": "string", "displayName": "Name"},
                    "status": {"dataType": "string", "displayName": "Status"},
                    "dept": {"dataType": "string", "displayName": "Department"},
                },
            },
        ),
        (
            "company",
            {
                "displayName": "Company",
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                    "name": {"dataType": "string", "displayName": "Name"},
                },
            },
        ),
    ):
        resp = client.put(f"/v2/ontologies/default/objectTypes/{api_name}", json=props)
        assert resp.status_code == 200, resp.text


def _seed_action_type(client: TestClient) -> None:
    body = {
        "displayName": "Promote Employee",
        "description": "Promote active employees",
        "targetObjectType": "employee",
        "parameters": {
            "message": {
                "apiName": "message",
                "dataType": "string",
                "displayName": "Message",
                "required": True,
            }
        },
        "submissionCriteria": [
            {
                "description": "Only active employees",
                "ruleLogic": "target_object['properties']['status'] == 'active'",
            }
        ],
        "validationRules": [],
        "executorKey": "system.log_message",
    }
    resp = client.put("/v2/ontologies/default/actionTypes/promote_employee", json=body)
    assert resp.status_code == 200, resp.text


def test_end_to_end_employee_lifecycle(client: TestClient):
    _put_employee_and_company(client)

    link_resp = client.put(
        "/v2/ontologies/default/linkTypes/works_for",
        json={
            "displayName": "Works For",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "has_employees", "displayName": "Has Employees"},
        },
    )
    assert link_resp.status_code == 200, link_resp.text

    employee_resp = client.put(
        "/v2/ontologies/default/objects/employee/e1",
        json={
            "properties": {
                "id": "e1",
                "name": "Alice",
                "status": "active",
                "dept": "ENG",
            }
        },
    )
    company_resp = client.put(
        "/v2/ontologies/default/objects/company/c1",
        json={"properties": {"id": "c1", "name": "Initech"}},
    )
    assert employee_resp.status_code == 200, employee_resp.text
    assert company_resp.status_code == 200, company_resp.text

    link_create = client.post(
        "/v2/ontologies/default/links/works_for",
        json={"fromPk": "e1", "toPk": "c1"},
    )
    assert link_create.status_code == 201, link_create.text

    traversal = client.get("/v2/ontologies/default/objects/employee/e1/works_for")
    assert traversal.status_code == 200
    traversal_payload = traversal.json()
    assert traversal_payload["data"][0]["objectTypeApiName"] == "company"

    search = client.get(
        "/v2/ontologies/default/objects",
        params={"objectType": "employee", "dept": "ENG"},
    )
    assert search.status_code == 200
    assert any(item["properties"]["name"] == "Alice" for item in search.json()["data"])

    _seed_action_type(client)
    actions = client.get("/v2/ontologies/default/objects/employee/e1/actions")
    assert actions.status_code == 200
    available = actions.json()["data"]
    assert any(act["apiName"] == "promote_employee" for act in available)

    exec_resp = client.post(
        "/v2/ontologies/default/objects/employee/e1/actions/promote_employee/execute",
        json={"parameters": {"message": "Promoted"}},
    )
    assert exec_resp.status_code == 200, exec_resp.text
    result = exec_resp.json()
    assert result.get("status") == "success"
    assert result.get("message") == "Promoted"
