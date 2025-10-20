from __future__ import annotations

from datetime import UTC, datetime

from ontologia_agent import AgentPlan, FileChange
from scripts.run_watcher_agent import _build_prompt, _to_record


def test_build_prompt_includes_event_details() -> None:
    events = [
        {
            "entityId": "customer:1",
            "objectType": "customer",
            "updatedAt": datetime.now(UTC).isoformat(),
        }
    ]

    prompt = _build_prompt(events, 10.0)

    assert "customer:1" in prompt
    assert "autonomous watch mode" in prompt


def test_to_record_serializes_plan() -> None:
    plan = AgentPlan(
        summary="Add premium flag",
        branch_name="feat/premium-flag",
        commit_message="feat: add premium flag",
        files=[
            FileChange(path="ontologia/object_types/customer.yml", contents="apiName: customer")
        ],
    )

    record = _to_record({"events": []}, plan)

    assert "generatedAt" in record
    assert record["plan"]["summary"] == "Add premium flag"
