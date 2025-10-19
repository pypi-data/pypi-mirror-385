from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

import httpx
import yaml

from ontologia_realtime.entity_manager import EntitySnapshot
from ontologia_realtime.journal import EntityEvent, EventStreamJournal

logger = logging.getLogger(__name__)


class ActionSink(Protocol):
    async def publish(self, result: DecisionResult) -> None:  # pragma: no cover - interface
        ...


class DecisionAuditLog(Protocol):
    async def record(self, result: DecisionResult) -> None:  # pragma: no cover - interface
        ...


@dataclass(slots=True, frozen=True)
class DecisionAction:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 0


@dataclass(slots=True, frozen=True)
class Condition:
    component: str
    field: str
    operator: str = "eq"
    value: Any = None

    def evaluate(self, snapshot: EntitySnapshot) -> tuple[bool, Any]:
        component_payload = snapshot.components.get(self.component)
        if component_payload is None:
            return False, None
        value = component_payload
        for segment in self.field.split("."):
            if isinstance(value, dict) and segment in value:
                value = value[segment]
            else:
                return False, None
        operator = self.operator.lower()
        target = self.value
        try:
            if operator == "eq":
                return value == target, value
            if operator == "ne":
                return value != target, value
            if operator == "gt":
                return value > target, value
            if operator == "gte":
                return value >= target, value
            if operator == "lt":
                return value < target, value
            if operator == "lte":
                return value <= target, value
            if operator == "contains":
                return target in value, value
            if operator == "in":
                return value in target, value
        except Exception:  # pragma: no cover - defensive guard
            logger.exception(
                "Failed to evaluate decision rule condition", extra={"operator": operator}
            )
            return False, None
        return False, value


@dataclass(slots=True, frozen=True)
class DecisionRule:
    name: str
    actions: tuple[DecisionAction, ...]
    conditions: tuple[Condition, ...] = ()
    condition_logic: str = "all"
    object_types: tuple[str, ...] | None = None
    provenances: tuple[str, ...] | None = None
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def applies_to(self, snapshot: EntitySnapshot) -> bool:
        if self.object_types and snapshot.object_type not in self.object_types:
            return False
        if self.provenances and snapshot.provenance not in self.provenances:
            return False
        return True

    def evaluate(self, snapshot: EntitySnapshot) -> tuple[bool, list[dict[str, Any]]]:
        if not self.conditions:
            return True, []
        evaluations: list[dict[str, Any]] = []
        matches: list[bool] = []
        for condition in self.conditions:
            passed, observed = condition.evaluate(snapshot)
            evaluations.append(
                {
                    "component": condition.component,
                    "field": condition.field,
                    "operator": condition.operator,
                    "expected": condition.value,
                    "observed": observed,
                    "matched": passed,
                }
            )
            matches.append(passed)
        logic = self.condition_logic.lower()
        if logic == "any":
            return any(matches), evaluations
        return all(matches), evaluations


@dataclass(slots=True, frozen=True)
class DecisionResult:
    rule_name: str
    entity_id: str
    object_type: str
    provenance: str
    actions: tuple[DecisionAction, ...]
    generated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    evaluations: tuple[dict[str, Any], ...] = ()


class InMemoryActionSink(ActionSink):
    def __init__(self) -> None:
        self.results: list[DecisionResult] = []

    async def publish(self, result: DecisionResult) -> None:
        self.results.append(result)


class JsonlDecisionAuditLog(DecisionAuditLog):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def record(self, result: DecisionResult) -> None:
        payload = {
            "rule_name": result.rule_name,
            "entity_id": result.entity_id,
            "object_type": result.object_type,
            "provenance": result.provenance,
            "generated_at": result.generated_at.isoformat(),
            "actions": [asdict(action) for action in result.actions],
            "metadata": result.metadata,
            "evaluations": list(result.evaluations),
        }

        def _write() -> None:
            with self._path.open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(payload, ensure_ascii=False) + "\n")

        await asyncio.to_thread(_write)


@dataclass(slots=True)
class DecisionConfig:
    rules_path: Path
    audit_log_path: Path | None = None
    actions_log_path: Path | None = None
    webhook_url: str | None = None
    webhook_timeout: float = 5.0
    ignore_replicated_events: bool = True


def load_rules_from_file(path: Path) -> tuple[DecisionRule, ...]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not data:
        return ()
    rules: list[DecisionRule] = []
    for item in data:
        condition_items = item.get("when", item.get("conditions", [])) or []
        conditions = tuple(
            Condition(
                component=condition["component"],
                field=condition["field"],
                operator=condition.get("operator", "eq"),
                value=condition.get("value"),
            )
            for condition in condition_items
        )
        action_items = item.get("actions", []) or []
        actions = tuple(
            DecisionAction(
                type=action["type"],
                payload=action.get("payload", {}),
                priority=action.get("priority", 0),
            )
            for action in action_items
        )
        rule = DecisionRule(
            name=item["name"],
            description=item.get("description"),
            object_types=tuple(item.get("object_types", [])) or None,
            provenances=tuple(item.get("provenances", [])) or None,
            actions=actions,
            conditions=conditions,
            condition_logic=item.get("logic", "all"),
            metadata=item.get("metadata", {}),
        )
        rules.append(rule)
    return tuple(rules)


class DecisionEngine:
    def __init__(self, rules: Sequence[DecisionRule]) -> None:
        self._rules = tuple(rules)

    def evaluate(
        self,
        snapshot: EntitySnapshot,
        *,
        event: EntityEvent | None = None,
    ) -> list[DecisionResult]:
        results: list[DecisionResult] = []
        for rule in self._rules:
            if not rule.applies_to(snapshot):
                continue
            matched, evaluations = rule.evaluate(snapshot)
            if not matched:
                continue
            metadata = dict(rule.metadata)
            if event is not None:
                metadata.update(
                    {
                        "sequence": event.sequence,
                        "event_type": event.event_type,
                        "updated_at": event.updated_at.isoformat(),
                        "replicated_from": event.metadata.get("replicated_from"),
                    }
                )
                metadata.update(event.metadata)
            results.append(
                DecisionResult(
                    rule_name=rule.name,
                    entity_id=snapshot.entity_id,
                    object_type=snapshot.object_type,
                    provenance=snapshot.provenance,
                    actions=rule.actions,
                    generated_at=datetime.now(UTC),
                    metadata=metadata,
                    evaluations=tuple(evaluations),
                )
            )
        return results


class JsonlActionSink(ActionSink):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def publish(self, result: DecisionResult) -> None:
        payload = {
            "rule_name": result.rule_name,
            "entity_id": result.entity_id,
            "actions": [asdict(action) for action in result.actions],
            "metadata": result.metadata,
            "generated_at": result.generated_at.isoformat(),
        }

        def _write() -> None:
            with self._path.open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(payload, ensure_ascii=False) + "\n")

        await asyncio.to_thread(_write)


class LoggingActionSink(ActionSink):
    async def publish(self, result: DecisionResult) -> None:
        logger.info(
            "Decision action",
            extra={
                "rule": result.rule_name,
                "entity_id": result.entity_id,
                "actions": [action.type for action in result.actions],
            },
        )


class WebhookActionSink(ActionSink):
    def __init__(self, url: str, *, timeout: float = 5.0) -> None:
        self._url = url
        self._timeout = timeout

    async def publish(self, result: DecisionResult) -> None:
        payload = {
            "rule": result.rule_name,
            "entityId": result.entity_id,
            "objectType": result.object_type,
            "provenance": result.provenance,
            "generatedAt": result.generated_at.isoformat(),
            "actions": [asdict(action) for action in result.actions],
            "metadata": result.metadata,
            "evaluations": list(result.evaluations),
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(self._url, json=payload)
                response.raise_for_status()
        except Exception:  # pragma: no cover - network guard
            logger.exception("Failed to deliver decision webhook", extra={"url": self._url})


class DecisionService:
    def __init__(
        self,
        event_stream: EventStreamJournal,
        engine: DecisionEngine,
        sink: ActionSink,
        *,
        audit_log: DecisionAuditLog | None = None,
        ignore_replicated: bool = True,
    ) -> None:
        self._event_stream = event_stream
        self._queue = event_stream.queue()
        self._engine = engine
        self._sink = sink
        self._audit_log = audit_log
        self._ignore_replicated = ignore_replicated
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._run(), name="realtime-decision-service")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None
        self._event_stream.unsubscribe(self._queue)

    async def _run(self) -> None:
        try:
            while True:
                event = await self._queue.get()
                if event.event_type not in {"upsert", "patch"}:
                    continue
                if self._ignore_replicated and event.metadata.get("replicated_from") is not None:
                    continue
                snapshot = EntitySnapshot(
                    entity_id=event.entity_id,
                    object_type=event.object_type,
                    provenance=event.provenance,
                    expires_at=event.expires_at,
                    components={key: dict(value) for key, value in event.components.items()},
                    updated_at=event.updated_at,
                )
                results = self._engine.evaluate(snapshot, event=event)
                for result in results:
                    await self._sink.publish(result)
                    if self._audit_log is not None:
                        await self._audit_log.record(result)
        except asyncio.CancelledError:  # pragma: no cover - shutdown path
            raise
        except Exception:  # pragma: no cover - resilience guard
            logger.exception("Decision service crashed")


class DecisionSimulator:
    def __init__(
        self,
        engine: DecisionEngine,
        *,
        audit_log: DecisionAuditLog | None = None,
    ) -> None:
        self._engine = engine
        self._audit_log = audit_log

    async def run(self, events: Iterable[EntityEvent]) -> list[DecisionResult]:
        results: list[DecisionResult] = []
        for event in events:
            snapshot = EntitySnapshot(
                entity_id=event.entity_id,
                object_type=event.object_type,
                provenance=event.provenance,
                expires_at=event.expires_at,
                components={key: dict(value) for key, value in event.components.items()},
                updated_at=event.updated_at,
            )
            evaluated = self._engine.evaluate(snapshot, event=event)
            for result in evaluated:
                results.append(result)
                if self._audit_log is not None:
                    await self._audit_log.record(result)
        return results


__all__ = [
    "ActionSink",
    "Condition",
    "DecisionAction",
    "DecisionAuditLog",
    "DecisionConfig",
    "DecisionEngine",
    "DecisionResult",
    "DecisionRule",
    "DecisionService",
    "DecisionSimulator",
    "InMemoryActionSink",
    "JsonlActionSink",
    "LoggingActionSink",
    "JsonlDecisionAuditLog",
    "WebhookActionSink",
    "load_rules_from_file",
]
