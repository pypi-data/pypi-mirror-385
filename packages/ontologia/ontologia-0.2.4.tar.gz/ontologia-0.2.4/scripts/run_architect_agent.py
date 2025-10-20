"""Run the Ontologia Architect agent against the MCP server."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ontologia.config import load_config


def _lazy_import_agents():
    try:
        from fastmcp.client import Client as MCPClient  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise SystemExit(
            "fastmcp is not installed. Install agent dependencies via `uv sync --group agents`."
        ) from exc

    try:
        from pydantic_ai import Agent  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise SystemExit(
            "pydantic-ai is not installed. Install agent dependencies via `uv sync --group agents`."
        ) from exc

    return MCPClient, Agent


class ActionPlan(BaseModel):
    """Structured response produced by the Architect agent."""

    tool_name: str
    arguments: dict[str, Any]
    justification: str


async def _gather_tools(client) -> str:
    tools = await client.list_tools()
    lines: list[str] = []
    for tool in tools:
        schema = json.dumps(tool.inputSchema, indent=2, sort_keys=True)
        description = tool.description or "No description provided."
        lines.append(f"- {tool.name}: {description}\n  schema: {schema}")
    catalog = "\n".join(lines)
    return catalog


async def run_architect_agent(prompt: str) -> None:
    mcp_client_cls, agent_cls = _lazy_import_agents()

    config = load_config(Path(os.getenv("ONTOLOGIA_CONFIG_ROOT", Path.cwd())))
    api_url = os.getenv("ONTOLOGIA_API_URL", config.api.base_url)
    mcp_url = os.getenv("ONTOLOGIA_MCP_URL", f"{api_url.rstrip('/')}/mcp")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY must be set to run the architect agent.")

    token = os.getenv("ONTOLOGIA_AGENT_TOKEN")
    if not token:
        raise SystemExit("ONTOLOGIA_AGENT_TOKEN must be set with a service account token.")

    auth_header = f"Bearer {token}"
    async with mcp_client_cls(mcp_url, auth=auth_header) as client:
        catalog_text = await _gather_tools(client)

        system_prompt = (
            "You are the Ontologia Architect agent. "
            "Select exactly one MCP tool to fulfill the user request. "
            "Respond with JSON matching the ActionPlan schema.\n\n"
            "Available tools:\n"
            f"{catalog_text}\n\n"
            "Rules:\n"
            "- tool_name must be one of the listed tools.\n"
            "- arguments must conform to the tool's JSON schema.\n"
            "- justification should briefly explain why the tool was chosen."
        )

        model_name = os.getenv("ONTOLOGIA_AGENT_MODEL", "openai:gpt-4o-mini")
        agent = agent_cls(
            model_name,
            output_type=ActionPlan,
            system_prompt=system_prompt,
            defer_model_check=True,
        )

        print("🤖 Agent thinking…\n")
        plan_result = await agent.run(prompt)
        plan = plan_result.output

        print("🛠️  Selected tool:", plan.tool_name)
        print("📋 Arguments:\n", json.dumps(plan.arguments, indent=2))

        call_result = await client.call_tool(plan.tool_name, plan.arguments)
        if call_result.is_error:
            print("❌ Tool call failed. See MCP logs for details.")
            return

        outcome = (
            call_result.data
            or call_result.structured_content
            or [getattr(block, "text", None) for block in call_result.content]
        )
        print("✅ Tool call succeeded. Outcome:\n", json.dumps(outcome, indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Ontologia Architect agent via the MCP server."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Crie um ObjectType 'product' com primary key 'sku' e propriedades obrigatórias 'sku' e 'name'.",
        help="Instruction for the agent (default: cria o ObjectType 'product').",
    )
    args = parser.parse_args()

    asyncio.run(run_architect_agent(args.prompt))


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
