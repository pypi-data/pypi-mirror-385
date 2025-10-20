from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from ontologia.domain.metamodels.types.action_type import ActionType


@pytest.fixture(autouse=True)
def _enable_temporal(monkeypatch):
    monkeypatch.setenv("USE_TEMPORAL_ACTIONS", "1")
    yield


class _FakeTemporalClient:
    async def execute_workflow(
        self, name: str, *, args: list[Any], **kwargs: Any
    ) -> dict[str, Any]:
        # Return a payload similar to system.log_message executor
        assert name == "ActionWorkflow"
        assert isinstance(args, (list, tuple)) and len(args) == 3
        _executor_key, _ctx, params = args
        # Ensure workflow id and task queue are passed
        assert "id" in kwargs and "task_queue" in kwargs
        return {"status": "success", "message": params.get("message")}


@pytest.fixture(autouse=True)
def _mock_temporal_client(monkeypatch):
    # Patch Client.connect to avoid real Temporal server
    async def _fake_connect(address: str, *, namespace: str):  # type: ignore[override]
        return _FakeTemporalClient()

    import temporalio.client as temporal_client  # type: ignore

    monkeypatch.setattr(temporal_client.Client, "connect", _fake_connect)
    yield


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


def test_actions_execute_via_temporal(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e1", "PENDING")
    _seed_action(session)

    r = client.post(
        "/v2/ontologies/default/objects/expense/e1/actions/approve_expense/execute",
        json={"parameters": {"message": "approved-via-temporal"}},
    )
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload.get("status") == "success"
    assert payload.get("message") == "approved-via-temporal"
