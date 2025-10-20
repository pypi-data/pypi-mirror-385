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


def _seed_action(session, api_name: str, *, executor_key: str, rule_logic: str | None = None):
    SQLModel.metadata.create_all(session.get_bind())
    act = ActionType(
        service="ontology",
        instance="default",
        api_name=api_name,
        display_name=api_name,
        description=None,
        target_object_type_api_name="expense",
        parameters={"message": {"dataType": "string", "displayName": "Message", "required": True}},
        submission_criteria=[],
        validation_rules=(
            [{"description": "rule", "rule_logic": rule_logic}] if rule_logic is not None else []
        ),
        executor_key=executor_key,
    )
    session.add(act)
    session.commit()
    session.refresh(act)
    return act


def test_execute_missing_required_param_returns_400(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e1", "PENDING")
    _seed_action(session, "approve_expense", executor_key="system.log_message")

    r = client.post(
        "/v2/ontologies/default/objects/expense/e1/actions/approve_expense/execute",
        json={"parameters": {}},
    )
    assert r.status_code == 400, r.text


def test_execute_with_unknown_executor_returns_501(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e2", "PENDING")
    _seed_action(session, "ghost_action", executor_key="system.unknown")

    r = client.post(
        "/v2/ontologies/default/objects/expense/e2/actions/ghost_action/execute",
        json={"parameters": {"message": "hi"}},
    )
    assert r.status_code == 501, r.text


def test_execute_validation_rule_failure_returns_400(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e3", "PENDING")
    _seed_action(
        session,
        "validate_msg_ok",
        executor_key="system.log_message",
        rule_logic="params['message'] == 'ok'",
    )

    r = client.post(
        "/v2/ontologies/default/objects/expense/e3/actions/validate_msg_ok/execute",
        json={"parameters": {"message": "nope"}},
    )
    assert r.status_code == 400, r.text
