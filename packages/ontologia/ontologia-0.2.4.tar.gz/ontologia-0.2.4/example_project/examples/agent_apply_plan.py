"""Apply a simple ontology change using the Architect agent engine.

Run this inside a sandbox created with ``ontologia-cli genesis``. The script reads local project
context from ``.ontologia/state.json`` and commits a new ObjectType definition on a feature branch.

Requires the optional agent dependencies:

```
uv sync --group agents
```
"""

from __future__ import annotations

import json
import secrets
from pathlib import Path

from ontologia_agent import AgentPlan, ArchitectAgent, FileChange, ProjectState


def _load_state(root: Path) -> ProjectState:
    state_path = root / ".ontologia" / "state.json"
    if not state_path.exists():
        raise SystemExit(
            "This script must run inside a sandbox created by `ontologia-cli genesis`."
        )

    data = json.loads(state_path.read_text(encoding="utf-8"))
    token = data.get("agent_token")
    if not token:
        raise SystemExit("Sandbox state missing agent token. Re-run `ontologia-cli genesis`.")

    return ProjectState(
        name=str(data.get("name") or root.name),
        root_path=root,
        api_url=str(data.get("api_url") or "http://127.0.0.1:8000"),
        mcp_url=str(data.get("mcp_url") or "http://127.0.0.1:8000/mcp"),
        agent_token=token,
        model_name=str(data.get("model_name") or "openai:gpt-4o-mini"),
    )


def main() -> None:
    root = Path.cwd()
    state = _load_state(root)

    try:
        agent = ArchitectAgent(state)
    except RuntimeError as exc:
        raise SystemExit(
            "Agent dependencies missing. Install them via `uv sync --group agents` before running this example."
        ) from exc

    target_path = "ontologia/object_types/sample_agent_object.yaml"
    full_path = state.root_path / target_path
    if full_path.exists():
        print(f"{target_path} already exists. Nothing to do.")
        return

    branch_name = f"feat/agent-sample-{secrets.token_hex(4)}"
    plan = AgentPlan(
        summary="Add sample Agent-driven ObjectType",
        branch_name=branch_name,
        commit_message="feat: add sample agent object",
        files=[
            FileChange(
                path=target_path,
                description="Sample ObjectType created by ontologia_agent example",
                contents=(
                    "apiName: sample_agent_object\n"
                    "displayName: Sample Agent Object\n"
                    "primaryKey: id\n"
                    "properties:\n"
                    "  id:\n"
                    "    dataType: string\n"
                    "    displayName: Identifier\n"
                    "    required: true\n"
                    "  note:\n"
                    "    dataType: string\n"
                    "    displayName: Note\n"
                ),
            )
        ],
    )

    written = agent.apply_plan(plan)
    if not written:
        print("Plan reported no changes.")
        return

    print(f"Created {target_path} on branch {branch_name}.")
    print("Review the commit, then run `ontologia-cli apply` or open a pull request.")


if __name__ == "__main__":
    main()
