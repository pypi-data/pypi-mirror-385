from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest
from git import Repo

from ontologia_agent import AgentPlan, ArchitectAgent, FileChange, ProjectState


@pytest.fixture()
def project_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProjectState:
    repo = Repo.init(tmp_path)
    (tmp_path / "README.md").write_text("seed", encoding="utf-8")
    repo.index.add(["README.md"])
    repo.index.commit("chore: seed repo")

    dummy_agent_cls = type("DummyAgent", (), {})
    dummy_client = type("DummyClient", (), {})
    monkeypatch.setattr(
        "ontologia_agent.engine._lazy_import_pydantic_ai",
        lambda: dummy_agent_cls,
    )
    monkeypatch.setattr(
        "ontologia_agent.engine._lazy_import_fastmcp",
        lambda: dummy_client,
    )

    return ProjectState(
        name="test",
        root_path=tmp_path,
        api_url="http://localhost:8000",
        mcp_url="http://localhost:8000/mcp",
        agent_token="dummy",  # noqa: S106 - test fixture token
    )


def test_apply_plan_creates_files_and_commits(project_state: ProjectState) -> None:
    agent = ArchitectAgent(project_state)

    plan = AgentPlan(
        summary="add sample object",
        branch_name="feat/sample-object",
        commit_message="feat: add sample object",
        files=[
            FileChange(
                path="ontologia/object_types/sample.yaml",
                contents="apiName: sample\ndisplayName: Sample",
            )
        ],
    )

    written = agent.apply_plan(plan)

    assert written, "plan should materialize files"
    created_path = project_state.root_path / "ontologia/object_types/sample.yaml"
    assert created_path.exists()
    assert created_path.read_text(encoding="utf-8").endswith("\n")

    repo = Repo(project_state.root_path)
    assert repo.active_branch.name == "feat/sample-object"
    assert repo.head.commit.message.strip() == "feat: add sample object"


def test_apply_plan_rejects_path_escape(project_state: ProjectState) -> None:
    agent = ArchitectAgent(project_state)
    plan = AgentPlan(
        summary="bad path",
        branch_name="feat/bad",
        commit_message="feat: bad",
        files=[FileChange(path="../outside.yaml", contents="bad: true")],
    )

    with pytest.raises(ValueError):
        agent.apply_plan(plan)


def test_run_pipeline_uses_mcp_tool(
    project_state: ProjectState, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeResult:
        is_error = False
        data = {"status": "ok", "returncode": 0}
        structured_content = None
        content = []

    class FakeClient:
        last_call: tuple[str, dict[str, Any]] | None = None

        def __init__(self, url: str, auth: str) -> None:
            self.url = url
            self.auth = auth

        async def __aenter__(self):  # noqa: D401
            return self

        async def __aexit__(self, exc_type, exc, tb):  # noqa: D401
            return False

        async def list_tools(self):  # noqa: D401
            return []

        async def call_tool(self, name: str, arguments: dict[str, Any]):  # noqa: D401
            FakeClient.last_call = (name, arguments)
            return FakeResult()

    monkeypatch.setattr(
        "ontologia_agent.engine._lazy_import_fastmcp",
        lambda: FakeClient,
    )
    monkeypatch.setattr(
        "ontologia_agent.engine._lazy_import_pydantic_ai",
        lambda: type("DummyAgent", (), {}),
    )

    agent = ArchitectAgent(project_state)
    result = asyncio.run(agent.run_pipeline(timeout_seconds=5))

    assert result["status"] == "ok"
    assert FakeClient.last_call == ("run_pipeline", {"timeout_seconds": 5})
