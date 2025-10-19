"""Engine that powers Ontologia interactive agents."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from ontologia_agent.models import AgentPlan, ProjectState
from ontologia_agent.prompts import architect_system_prompt
from ontologia_agent.skills import FilesystemSkill, GitSkill


def _lazy_import_pydantic_ai():
    try:
        from pydantic_ai import Agent  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "pydantic-ai is not installed. Install agent dependencies via `uv sync --group agents`."
        ) from exc

    return Agent


def _lazy_import_fastmcp():
    try:
        from fastmcp.client import Client as MCPClient  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "fastmcp is not installed. Install agent dependencies via `uv sync --group agents`."
        ) from exc

    return MCPClient


class ArchitectAgent:
    """High-level orchestrator that collaborates with large language models."""

    def __init__(self, state: ProjectState) -> None:
        self.state = state
        self.fs = FilesystemSkill(state.root_path)
        self.git = GitSkill(state.root_path)
        self.AgentCls = _lazy_import_pydantic_ai()
        self.MCPClient = _lazy_import_fastmcp()

    async def _fetch_tool_catalog(self) -> str:
        token = self.state.agent_token
        auth_header = f"Bearer {token}"
        async with self.MCPClient(self.state.mcp_url, auth=auth_header) as client:
            tools = await client.list_tools()
            lines: list[str] = []
            for tool in tools:
                description = tool.description or "No description provided"
                schema = json.dumps(tool.inputSchema, indent=2, sort_keys=True)
                lines.append(f"- {tool.name}: {description}\n  schema: {schema}")
            return "\n".join(lines) or "(no tools discovered)"

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        token = self.state.agent_token
        auth_header = f"Bearer {token}"
        async with self.MCPClient(self.state.mcp_url, auth=auth_header) as client:
            result = await client.call_tool(name, arguments)
            if result.is_error:
                raise RuntimeError(f"Tool {name} failed: {result.error}")
            return (
                result.data
                or result.structured_content
                or [getattr(block, "text", None) for block in result.content]
            )

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        return await self._call_tool(name, arguments)

    async def create_plan(self, user_prompt: str) -> AgentPlan:
        """Generate a plan using the backing LLM."""

        tool_catalog = "(tool catalog unavailable)"
        try:
            tool_catalog = await self._fetch_tool_catalog()
        except Exception as exc:  # pragma: no cover - network optional
            tool_catalog = f"Failed to fetch tool catalog: {exc}"

        obj_catalog, link_catalog = self.fs.describe_catalog()
        system_prompt = architect_system_prompt(tool_catalog, obj_catalog, link_catalog)

        agent = self.AgentCls(
            self.state.model_name,
            output_type=AgentPlan,
            system_prompt=system_prompt,
            defer_model_check=True,
        )

        result = await agent.run(user_prompt)
        plan: AgentPlan = result.output
        return plan

    async def run_pipeline(self, timeout_seconds: int = 1800) -> dict[str, Any]:
        payload = await self.call_tool("run_pipeline", {"timeout_seconds": timeout_seconds})
        if isinstance(payload, list):  # pragma: no cover - defensive
            return {"status": "error", "stdout": "", "stderr": "Unexpected payload", "raw": payload}
        return dict(payload)

    def apply_plan(
        self,
        plan: AgentPlan,
        *,
        author_name: str | None = None,
        author_email: str | None = None,
    ) -> list[Path]:
        if plan.is_empty():
            return []

        self.fs.ensure_structure()
        self.git.ensure_branch(plan.branch_name)

        written_paths: list[Path] = []
        for change in plan.files:
            path = self._validate_path(change.path)
            text = change.contents.rstrip() + "\n"
            destination = self.fs.write_file(path, text)
            written_paths.append(destination)

        self.git.stage(written_paths)
        self.git.commit(plan.commit_message, author=author_name, email=author_email)
        return written_paths

    def _validate_path(self, relative_path: str) -> str:
        normalized = Path(relative_path)
        if normalized.is_absolute():
            raise ValueError(f"Agent attempted to write absolute path: {relative_path}")
        full = (self.state.root_path / normalized).resolve()
        if not str(full).startswith(str(self.state.root_path.resolve())):
            raise ValueError(f"Agent attempted to escape project root: {relative_path}")
        return str(normalized)


# Convenience synchronous wrappers -------------------------------------------------


def plan_with_agent(state: ProjectState, prompt: str) -> AgentPlan:
    agent = ArchitectAgent(state)
    return asyncio.run(agent.create_plan(prompt))


def apply_plan(state: ProjectState, plan: AgentPlan) -> list[Path]:
    agent = ArchitectAgent(state)
    return agent.apply_plan(plan)
