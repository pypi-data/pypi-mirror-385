from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ontologia_agent import ArchitectAgent
from ontologia_cli.main import _load_project_state


def _build_prompt(events: list[dict[str, Any]], window_seconds: float) -> str:
    events_json = json.dumps(events, indent=2, default=str)
    return (
        "You are operating in autonomous watch mode. The following real-time events were captured "
        f"during the last {window_seconds:.1f} seconds:\n{events_json}\n\n"
        "Analyze these events. If they reveal an emerging property, new entity relationship, or "
        "other ontology drift, produce an AgentPlan that addresses the issue (YAML updates, dbt "
        "models, migrations, pipeline run). If no action is needed, return an empty plan with the "
        "summary 'Nenhuma ação necessária'."
    )


def _write_plan(output_dir: Path, plan_payload: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    branch = plan_payload["plan"].get("branch_name", "plan")
    safe_branch = branch.replace("/", "-")[:64]
    file_path = output_dir / f"plan_{timestamp}_{safe_branch}.json"
    file_path.write_text(json.dumps(plan_payload, indent=2), encoding="utf-8")
    return file_path


async def _collect_events(agent: ArchitectAgent, args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "duration_seconds": args.duration,
        "max_events": args.max_events,
    }
    if args.object_type:
        payload["object_types"] = args.object_type
    if args.entity_id:
        payload["entity_ids"] = args.entity_id
    result = await agent.call_tool("stream_ontology_events", payload)
    if isinstance(result, list):
        # Defensive: ensure consistent shape
        return {"events": result, "count": len(result), "durationSeconds": args.duration}
    return dict(result)


def _to_record(events: dict[str, Any], plan) -> dict[str, Any]:
    return {
        "generatedAt": datetime.now(UTC).isoformat(),
        "events": events,
        "plan": plan.model_dump(mode="json"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ArchitectAgent in watcher mode")
    parser.add_argument(
        "--interval", type=float, default=300.0, help="Sleep interval between scans (seconds)"
    )
    parser.add_argument(
        "--duration", type=float, default=15.0, help="Window to capture events (seconds)"
    )
    parser.add_argument("--max-events", type=int, default=50, help="Maximum events per window")
    parser.add_argument(
        "--object-type", action="append", dest="object_type", help="Filter events by object type"
    )
    parser.add_argument(
        "--entity-id", action="append", dest="entity_id", help="Filter events by entity id"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("plans_for_review"),
        help="Directory to store generated plans",
    )
    parser.add_argument("--model", type=str, default=None, help="Override LLM model name")
    parser.add_argument("--once", action="store_true", help="Run a single iteration and exit")
    args = parser.parse_args()

    try:
        state = _load_project_state(model_override=args.model)
    except SystemExit as exc:  # _load_project_state may call typer.Exit
        code = exc.code if isinstance(exc.code, int) else 1
        print("Failed to load project state. Ensure 'ontologia genesis' has been executed.")
        sys.exit(code)

    agent = ArchitectAgent(state)
    print(
        f"Watcher agent connected to project '{state.name}'. Streaming events every {args.interval:.1f}s."
    )

    try:
        while True:
            events_payload = asyncio.run(_collect_events(agent, args))
            events = events_payload.get("events") or []
            if not events:
                print("No events observed during this window.")
            else:
                prompt = _build_prompt(events, events_payload.get("durationSeconds", args.duration))
                print(f"Captured {len(events)} event(s). Generating analysis plan…")
                plan = asyncio.run(agent.create_plan(prompt))
                if plan.is_empty():
                    print("Agent concluded that no action is required.")
                else:
                    record = _to_record(events_payload, plan)
                    target = _write_plan(args.output_dir, record)
                    print(f"Proposed plan saved to {target}. Awaiting human review.")
            if args.once:
                break
            time.sleep(max(args.interval, 1.0))
    except KeyboardInterrupt:
        print("Watcher interrupted by user. Exiting.")


if __name__ == "__main__":
    main()
