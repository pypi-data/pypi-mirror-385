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


class _FakeHandle:
    def __init__(self):
        self.run_id = "run-123"


class _FakeTemporalClient:
    async def start_workflow(self, name: str, *, args: list[Any], **kwargs: Any):
        assert name == "ActionWorkflow"
        assert isinstance(args, (list, tuple)) and len(args) == 3
        # Ensure identifiers are passed
        assert "id" in kwargs and kwargs.get("id")
        assert "task_queue" in kwargs and kwargs.get("task_queue")
        return _FakeHandle()


@pytest.fixture(autouse=True)
def _mock_temporal_client(monkeypatch):
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


def test_actions_start_returns_ids(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e1", "PENDING")
    _seed_action(session)

    r = client.post(
        "/v2/ontologies/default/objects/expense/e1/actions/approve_expense/start",
        json={"parameters": {"message": "approved"}},
    )
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload.get("status") == "started"
    assert payload.get("workflowId")
    assert payload.get("runId") == "run-123"
