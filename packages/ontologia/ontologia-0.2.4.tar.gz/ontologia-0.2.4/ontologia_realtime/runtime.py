from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ontologia_realtime.decision import (
    ActionSink,
    DecisionConfig,
    DecisionEngine,
    DecisionService,
    JsonlActionSink,
    JsonlDecisionAuditLog,
    LoggingActionSink,
    WebhookActionSink,
    load_rules_from_file,
)
from ontologia_realtime.entity_manager import EntityManager, EntitySnapshot
from ontologia_realtime.journal import (
    CompositeEntityJournal,
    EntityEvent,
    EntityStoreJournal,
    EventStreamJournal,
    JsonlEntityJournal,
)
from ontologia_realtime.replication import EntityReplicator, ReplicationConfig, TLSConfig
from ontologia_realtime.schema import SchemaRegistry
from ontologia_realtime.storage import SQLiteEntityStore

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RealTimeRuntimeConfig:
    node_id: str
    store_path: Path
    journal_path: Path
    prune_interval_seconds: int = 5
    replication: ReplicationConfig | None = None
    tls: TLSConfig | None = None
    decision: DecisionConfig | None = None


class RealTimeRuntime:
    def __init__(
        self,
        config: RealTimeRuntimeConfig,
        *,
        schema_registry: SchemaRegistry | None = None,
    ) -> None:
        self._config = config
        self._store = SQLiteEntityStore(config.store_path)
        self._event_stream = EventStreamJournal()
        journals = [
            EntityStoreJournal(self._store),
            self._event_stream,
            JsonlEntityJournal(config.journal_path),
        ]
        self._manager = EntityManager(
            schema_registry=schema_registry, journal=CompositeEntityJournal(journals)
        )
        self._replicator = (
            EntityReplicator(self._event_stream, config.replication, tls=config.tls)
            if config.replication is not None
            else None
        )
        self._decision_service = self._build_decision_service(config.decision)
        self._prune_task: asyncio.Task[None] | None = None
        self._started = False

    @property
    def manager(self) -> EntityManager:
        return self._manager

    async def start(self) -> None:
        if self._started:
            return
        snapshots = await self._store.load_snapshots()
        if snapshots:
            await self._manager.load_snapshots(self._normalize_snapshots(snapshots))
        if self._replicator is not None:
            await self._replicator.start()
        if self._decision_service is not None:
            await self._decision_service.start()
        self._prune_task = asyncio.create_task(self._prune_loop(), name="realtime-prune-loop")
        self._started = True

    async def stop(self) -> None:
        if not self._started:
            return
        if self._prune_task:
            self._prune_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._prune_task
            self._prune_task = None
        if self._replicator is not None:
            await self._replicator.stop()
        if self._decision_service is not None:
            await self._decision_service.stop()
        self._started = False

    async def _prune_loop(self) -> None:
        try:
            while True:
                await self._manager.prune_expired()
                await asyncio.sleep(self._config.prune_interval_seconds)
        except asyncio.CancelledError:  # pragma: no cover - shutdown path
            raise

    def _normalize_snapshots(self, snapshots: Iterable[EntitySnapshot]) -> list[EntitySnapshot]:
        # Entities loaded from storage already carry normalized components
        return list(snapshots)

    def subscribe_events(self) -> asyncio.Queue[EntityEvent]:
        return self._event_stream.queue()

    def unsubscribe_events(self, queue: asyncio.Queue[EntityEvent]) -> None:
        self._event_stream.unsubscribe(queue)

    async def get_recent_events(
        self,
        *,
        limit: int = 100,
        object_types: set[str] | None = None,
        entity_ids: set[str] | None = None,
    ) -> list[EntityEvent]:
        return await asyncio.to_thread(
            self._read_recent_events,
            limit,
            object_types,
            entity_ids,
        )

    def _build_decision_service(self, config: DecisionConfig | None) -> DecisionService | None:
        if config is None:
            return None
        rules = load_rules_from_file(config.rules_path)
        if not rules:
            logger.warning(
                "Decision service enabled but no rules found",
                extra={"path": str(config.rules_path)},
            )
            return None
        engine = DecisionEngine(rules)
        audit_log = (
            JsonlDecisionAuditLog(config.audit_log_path)
            if config.audit_log_path is not None
            else None
        )
        sink: ActionSink
        if config.webhook_url:
            sink = WebhookActionSink(config.webhook_url, timeout=config.webhook_timeout)
        elif config.actions_log_path is not None:
            sink = JsonlActionSink(config.actions_log_path)
        else:
            sink = LoggingActionSink()
        return DecisionService(
            self._event_stream,
            engine,
            sink,
            audit_log=audit_log,
            ignore_replicated=config.ignore_replicated_events,
        )

    def _read_recent_events(
        self,
        limit: int,
        object_types: set[str] | None,
        entity_ids: set[str] | None,
    ) -> list[EntityEvent]:
        if limit <= 0:
            return []
        path = self._config.journal_path
        if not path.exists():
            return []
        buffer: deque[str] = deque(maxlen=limit)
        with path.open("r", encoding="utf-8") as fp:
            for line in fp:
                buffer.append(line.strip())
        events: list[EntityEvent] = []
        for raw in buffer:
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:  # pragma: no cover - corrupted entry
                continue
            try:
                event = EntityEvent.from_dict(payload)
            except Exception:  # pragma: no cover - resilience guard
                logger.exception("Failed to parse event from journal", extra={"payload": payload})
                continue
            if object_types and event.object_type not in object_types:
                continue
            if entity_ids and event.entity_id not in entity_ids:
                continue
            events.append(event)
        return events


__all__ = ["RealTimeRuntime", "RealTimeRuntimeConfig"]
