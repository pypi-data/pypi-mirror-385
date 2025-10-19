from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _enable_temporal(monkeypatch):
    monkeypatch.setenv("USE_TEMPORAL_ACTIONS", "1")
    yield


class _FakeHandle:
    def __init__(self, run_id: str = "run-xyz"):
        self.run_id = run_id

    async def describe(self):
        return {"run_id": self.run_id, "status": "RUNNING"}


class _FakeTemporalClient:
    def get_workflow_handle(self, workflow_id: str, run_id: str | None = None):
        return _FakeHandle(run_id or "run-xyz")


@pytest.fixture(autouse=True)
def _mock_temporal_client(monkeypatch):
    async def _fake_connect(address: str, *, namespace: str):  # type: ignore[override]
        return _FakeTemporalClient()

    import temporalio.client as temporal_client  # type: ignore

    monkeypatch.setattr(temporal_client.Client, "connect", _fake_connect)
    yield


def test_actions_run_status(client: TestClient):
    r = client.get("/v2/ontologies/default/actions/runs/wf-123?runId=run-xyz")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["workflowId"] == "wf-123"
    assert data["runId"] == "run-xyz"
    assert data["status"].upper() in {"RUNNING", "UNKNOWN"}
