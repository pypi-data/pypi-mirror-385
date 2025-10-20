from fastapi.testclient import TestClient


def test_action_type_crud(client: TestClient):
    # create ObjectType used by ActionType target
    r = client.put(
        "/v2/ontologies/default/objectTypes/expense",
        json={
            "displayName": "Expense",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "status": {"dataType": "string", "displayName": "Status", "required": False},
            },
        },
    )
    assert r.status_code == 200

    # upsert action type
    body = {
        "displayName": "Approve Expense",
        "description": "Approve expense when pending",
        "targetObjectType": "expense",
        "parameters": {
            "message": {"dataType": "string", "displayName": "Message", "required": True}
        },
        "submissionCriteria": [
            {
                "description": "Only when pending",
                "ruleLogic": "target_object['properties']['status']=='PENDING'",
            }
        ],
        "validationRules": [],
        "executorKey": "system.log_message",
    }
    r2 = client.put("/v2/ontologies/default/actionTypes/approve_expense", json=body)
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert data["apiName"] == "approve_expense"
    assert data["targetObjectType"] == "expense"
    assert data["version"] == 1
    assert data["isLatest"] is True

    # get it
    r3 = client.get("/v2/ontologies/default/actionTypes/approve_expense")
    assert r3.status_code == 200

    # list
    r4 = client.get("/v2/ontologies/default/actionTypes")
    assert r4.status_code == 200
    lst = r4.json()["data"]
    assert any(it["apiName"] == "approve_expense" and it["version"] == 1 for it in lst)

    # delete
    r5 = client.delete("/v2/ontologies/default/actionTypes/approve_expense")
    assert r5.status_code == 204

    # get after delete -> 404
    r6 = client.get("/v2/ontologies/default/actionTypes/approve_expense")
    assert r6.status_code == 404
