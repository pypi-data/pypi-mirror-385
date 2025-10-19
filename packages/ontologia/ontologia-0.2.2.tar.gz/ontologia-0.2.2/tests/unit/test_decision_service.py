from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from ontologia_realtime.decision import (
    Condition,
    DecisionAction,
    DecisionEngine,
    DecisionRule,
    DecisionService,
    DecisionSimulator,
    InMemoryActionSink,
    WebhookActionSink,
    load_rules_from_file,
)
from ontologia_realtime.entity_manager import EntitySnapshot
from ontologia_realtime.journal import EntityEvent, EventStreamJournal

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_load_rules_from_file(tmp_path):
    rules_path = tmp_path / "rules.yaml"
    rules_path.write_text(
        """
- name: escalate-temperature
  object_types: ["sensor"]
  logic: all
  when:
    - component: telemetry
      field: temperature
      operator: gt
      value: 80
  actions:
    - type: alert
      payload:
        severity: high
""",
        encoding="utf-8",
    )
    rules = load_rules_from_file(rules_path)
    assert len(rules) == 1
    rule = rules[0]
    assert rule.name == "escalate-temperature"
    assert rule.object_types == ("sensor",)
    assert rule.actions[0].payload["severity"] == "high"


def _build_snapshot() -> EntityEvent:
    now = datetime.now(UTC)
    return EntityEvent(
        sequence=1,
        event_type="upsert",
        entity_id="sensor-1",
        object_type="sensor",
        provenance="ingest",
        components={"telemetry": {"temperature": 90}},
        expires_at=now + timedelta(minutes=5),
        updated_at=now,
        metadata={},
    )


def test_decision_engine_matches_conditions():
    rule = DecisionRule(
        name="high-temp",
        object_types=("sensor",),
        actions=(DecisionAction(type="alert", payload={"severity": "high"}),),
        conditions=(
            Condition(component="telemetry", field="temperature", operator="gt", value=80),
        ),
    )
    engine = DecisionEngine([rule])
    event = _build_snapshot()
    results = engine.evaluate(
        snapshot=event_to_snapshot(event),
        event=event,
    )
    assert len(results) == 1
    assert results[0].actions[0].type == "alert"
    assert results[0].metadata["sequence"] == 1


def event_to_snapshot(event: EntityEvent) -> EntitySnapshot:
    return EntitySnapshot(
        entity_id=event.entity_id,
        object_type=event.object_type,
        provenance=event.provenance,
        expires_at=event.expires_at,
        components={key: dict(value) for key, value in event.components.items()},
        updated_at=event.updated_at,
    )


class _AuditLog:
    def __init__(self) -> None:
        self.results: list[str] = []

    async def record(self, result):
        self.results.append(result.rule_name)


async def _wait_for(predicate, *, timeout: float) -> None:
    async def _poll() -> None:
        while not predicate():
            await asyncio.sleep(0.01)

    await asyncio.wait_for(_poll(), timeout=timeout)


@pytest.mark.anyio
async def test_decision_service_dispatches_actions():
    event_stream = EventStreamJournal()
    rule = DecisionRule(
        name="high-temp",
        object_types=("sensor",),
        actions=(DecisionAction(type="alert", payload={"severity": "high"}),),
        conditions=(
            Condition(component="telemetry", field="temperature", operator="gt", value=80),
        ),
    )
    engine = DecisionEngine([rule])
    sink = InMemoryActionSink()
    audit = _AuditLog()
    service = DecisionService(
        event_stream,
        engine,
        sink,
        audit_log=audit,
        ignore_replicated=False,
    )
    await service.start()
    await event_stream.record(_build_snapshot())
    await _wait_for(lambda: bool(sink.results), timeout=1)
    await service.stop()
    assert sink.results
    assert audit.results == ["high-temp"]


@pytest.mark.anyio
async def test_decision_simulator_runs_scenario():
    rule = DecisionRule(
        name="high-temp",
        object_types=("sensor",),
        actions=(DecisionAction(type="alert", payload={"severity": "critical"}),),
        conditions=(
            Condition(component="telemetry", field="temperature", operator="gt", value=80),
        ),
    )
    engine = DecisionEngine([rule])
    simulator = DecisionSimulator(engine)
    results = await simulator.run([_build_snapshot()])
    assert len(results) == 1
    assert results[0].actions[0].payload["severity"] == "critical"


@pytest.mark.anyio
async def test_webhook_action_sink_invokes_http_client(monkeypatch):
    captured: dict[str, Any] = {}

    class _MockResponse:
        def raise_for_status(self) -> None:
            return None

    class _MockClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def post(self, url, json):
            captured["url"] = url
            captured["json"] = json
            return _MockResponse()

    monkeypatch.setattr("ontologia_realtime.decision.httpx.AsyncClient", _MockClient)

    sink = WebhookActionSink("https://example.test/webhook", timeout=1.0)
    rule = DecisionRule(
        name="webhook",
        object_types=("sensor",),
        actions=(DecisionAction(type="alert", payload={"severity": "high"}),),
        conditions=(
            Condition(component="telemetry", field="temperature", operator="gt", value=80),
        ),
    )
    engine = DecisionEngine([rule])
    event = _build_snapshot()
    result = engine.evaluate(event_to_snapshot(event), event=event)[0]
    await sink.publish(result)
    assert captured["url"] == "https://example.test/webhook"
    assert captured["json"]["rule"] == "webhook"
