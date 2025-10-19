from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from ontologia.domain.metamodels.types.action_type import ActionType


def _put_expense_object_type(client: TestClient):
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
    assert r.status_code == 200, r.text


def _put_expense(client: TestClient, pk: str, status: str):
    r = client.put(
        f"/v2/ontologies/default/objects/expense/{pk}",
        json={"properties": {"id": pk, "status": status}},
    )
    assert r.status_code == 200, r.text


def _seed_action(session):
    # ensure table exists for the in-memory engine
    SQLModel.metadata.create_all(session.get_bind())
    act = ActionType(
        service="ontology",
        instance="default",
        api_name="approve_expense",
        display_name="Approve Expense",
        description="Approve expense when pending",
        target_object_type_api_name="expense",
        parameters={"message": {"dataType": "string", "displayName": "Message", "required": True}},
        submission_criteria=[
            {
                "description": "Only when pending",
                "rule_logic": "target_object['properties']['status'] == 'PENDING'",
            }
        ],
        validation_rules=[],
        executor_key="system.log_message",
    )
    session.add(act)
    session.commit()
    session.refresh(act)
    return act


def test_actions_discovery_and_execute(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e1", "PENDING")
    _seed_action(session)

    # Discover
    r = client.get("/v2/ontologies/default/objects/expense/e1/actions")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert [a["apiName"] for a in data] == ["approve_expense"]

    # Execute
    r2 = client.post(
        "/v2/ontologies/default/objects/expense/e1/actions/approve_expense/execute",
        json={"parameters": {"message": "approved"}},
    )
    assert r2.status_code == 200, r2.text
    payload = r2.json()
    assert payload.get("status") == "success"
    assert payload.get("message") == "approved"


def test_actions_unavailable_when_criteria_fail(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e2", "DRAFT")
    _seed_action(session)

    # Discover: none
    r = client.get("/v2/ontologies/default/objects/expense/e2/actions")
    assert r.status_code == 200, r.text
    assert r.json()["data"] == []

    # Execute: 403
    r2 = client.post(
        "/v2/ontologies/default/objects/expense/e2/actions/approve_expense/execute",
        json={"parameters": {"message": "nope"}},
    )
    assert r2.status_code == 403
