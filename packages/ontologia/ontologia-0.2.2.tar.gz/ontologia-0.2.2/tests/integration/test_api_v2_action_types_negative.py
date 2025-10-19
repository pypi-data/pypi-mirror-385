from fastapi.testclient import TestClient


def test_upsert_action_type_with_invalid_rule_returns_400(client: TestClient):
    # ensure target object type exists
    r = client.put(
        "/v2/ontologies/default/objectTypes/expense",
        json={
            "displayName": "Expense",
            "primaryKey": "id",
            "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
        },
    )
    assert r.status_code == 200, r.text

    body = {
        "displayName": "Bad Rule Action",
        "targetObjectType": "expense",
        "parameters": {},
        "submissionCriteria": [{"description": "bad", "ruleLogic": "this is not python"}],
        "validationRules": [],
        "executorKey": "system.log_message",
    }

    r2 = client.put("/v2/ontologies/default/actionTypes/bad_rule", json=body)
    assert r2.status_code == 400, r2.text
    # Accept either invalid syntax or unsupported construct message from validator
    assert (
        "Invalid submissionCriteria rule expression" in r2.text
        or "Unsupported submissionCriteria rule expression" in r2.text
    )
