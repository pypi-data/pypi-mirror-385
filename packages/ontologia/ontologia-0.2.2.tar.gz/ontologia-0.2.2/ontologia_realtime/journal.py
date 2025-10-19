from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from asyncio import Queue

    from ontologia_realtime.storage import EntityStore


@dataclass(slots=True, frozen=True)
class EntityEvent:
    """Append-only log entry describing a state transition for an entity."""

    sequence: int
    event_type: str
    entity_id: str
    object_type: str
    provenance: str
    components: dict[str, dict[str, Any]]
    expires_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> EntityEvent:
        expires_at_raw = payload.get("expires_at")
        updated_at_raw = payload.get("updated_at")
        expires_at = cls._parse_datetime(expires_at_raw)
        updated_at = cls._parse_datetime(updated_at_raw)
        components = {key: dict(value) for key, value in payload.get("components", {}).items()}
        metadata = dict(payload.get("metadata", {}))
        return cls(
            sequence=payload["sequence"],
            event_type=payload["event_type"],
            entity_id=payload["entity_id"],
            object_type=payload["object_type"],
            provenance=payload["provenance"],
            components=components,
            expires_at=expires_at,
            updated_at=updated_at,
            metadata=metadata,
        )

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime:
        if value is None:
            return datetime.now(UTC)
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)


class EntityJournal(Protocol):
    """Abstraction over append-only event storage backends."""

    async def record(self, event: EntityEvent) -> None:  # pragma: no cover - interface
        ...


class InMemoryEntityJournal:
    """Test-friendly journal that retains events in memory."""

    def __init__(self) -> None:
        self._events: list[EntityEvent] = []

    @property
    def events(self) -> list[EntityEvent]:
        return list(self._events)

    async def record(self, event: EntityEvent) -> None:
        self._events.append(event)


class JsonlEntityJournal:
    """Persists events as JSON Lines on local disk."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def record(self, event: EntityEvent) -> None:
        payload = {
            "sequence": event.sequence,
            "event_type": event.event_type,
            "entity_id": event.entity_id,
            "object_type": event.object_type,
            "provenance": event.provenance,
            "components": event.components,
            "expires_at": event.expires_at.isoformat(),
            "updated_at": event.updated_at.isoformat(),
            "metadata": event.metadata,
        }

        def _write() -> None:
            with self._path.open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(payload, ensure_ascii=False) + "\n")

        try:
            await asyncio.to_thread(_write)
        except Exception:  # pragma: no cover - I/O safety guard
            logger.exception("Failed to persist entity event", extra={"event": payload})


class CompositeEntityJournal(EntityJournal):
    """Fan-out journal that records events across multiple sinks."""

    def __init__(self, journals: Iterable[EntityJournal]) -> None:
        self._journals = list(journals)

    async def record(self, event: EntityEvent) -> None:
        for journal in self._journals:
            try:
                await journal.record(event)
            except Exception:  # pragma: no cover - follower failures should not break pipeline
                logger.exception("Failed to record event in journal %s", journal.__class__.__name__)


class EntityStoreJournal(EntityJournal):
    """Persists events into an EntityStore."""

    def __init__(self, store: EntityStore) -> None:
        self._store = store

    async def record(self, event: EntityEvent) -> None:
        await self._store.apply_event(event)


class EventStreamJournal(EntityJournal):
    """Provides a bounded async queue of events for consumers."""

    def __init__(self, *, maxsize: int = 2048) -> None:
        self._maxsize = maxsize
        self._queues: list[Queue[EntityEvent]] = []

    async def record(self, event: EntityEvent) -> None:
        to_remove: list[Queue[EntityEvent]] = []
        for queue in list(self._queues):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:  # pragma: no cover - backpressure safeguard
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:  # pragma: no cover - subscriber overwhelmed
                    to_remove.append(queue)
            except RuntimeError:  # pragma: no cover - queue likely garbage collected
                to_remove.append(queue)
        for queue in to_remove:
            with contextlib.suppress(ValueError):
                self._queues.remove(queue)

    def queue(self) -> Queue[EntityEvent]:
        queue: Queue[EntityEvent] = asyncio.Queue(maxsize=self._maxsize)
        self._queues.append(queue)
        return queue

    def unsubscribe(self, queue: Queue[EntityEvent]) -> None:
        with contextlib.suppress(ValueError):
            self._queues.remove(queue)


__all__ = [
    "CompositeEntityJournal",
    "EntityEvent",
    "EntityJournal",
    "EntityStoreJournal",
    "EventStreamJournal",
    "InMemoryEntityJournal",
    "JsonlEntityJournal",
]
