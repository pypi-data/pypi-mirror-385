from __future__ import annotations

import asyncio
import itertools
import logging
from asyncio import QueueEmpty
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from ontologia_realtime.journal import EntityEvent, EntityJournal
from ontologia_realtime.schema import SchemaRegistry

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class EntitySnapshot:
    """In-memory representation of an entity tracked by the real-time layer."""

    entity_id: str
    object_type: str
    provenance: str
    expires_at: datetime
    components: dict[str, dict[str, Any]] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_expired(self, *, at: datetime | None = None) -> bool:
        comparison = at or datetime.now(UTC)
        return comparison >= self.expires_at


class EntityManager:
    """Thread-safe entity registry supporting watchers and TTL-based expiry."""

    def __init__(
        self,
        *,
        subscriber_queue_size: int = 1024,
        schema_registry: SchemaRegistry | None = None,
        journal: EntityJournal | None = None,
    ) -> None:
        self._entities: dict[str, EntitySnapshot] = {}
        self._lock = asyncio.Lock()
        self._subscribers: dict[
            int, tuple[asyncio.Queue[EntitySnapshot | None], set[str] | None]
        ] = {}
        self._id_counter = itertools.count(1)
        self._event_counter = itertools.count(1)
        self._subscriber_queue_size = subscriber_queue_size
        self._schema_registry = schema_registry
        self._journal = journal

    async def upsert(
        self,
        entity_id: str,
        *,
        object_type: str,
        provenance: str,
        ttl: timedelta,
        components: Mapping[str, Mapping[str, Any]],
        metadata: Mapping[str, Any] | None = None,
    ) -> EntitySnapshot:
        """Insert or update an entity and notify subscribers."""

        if ttl.total_seconds() <= 0:
            raise ValueError("TTL must be positive")

        now = datetime.now(UTC)
        expires_at = now + ttl
        normalized_components = self._normalize_components(object_type, components)
        async with self._lock:
            existing = self._entities.get(entity_id)
            if existing is None:
                snapshot = EntitySnapshot(
                    entity_id=entity_id,
                    object_type=object_type,
                    provenance=provenance,
                    expires_at=expires_at,
                    components=normalized_components,
                    updated_at=now,
                )
            else:
                merged_components = {key: dict(value) for key, value in existing.components.items()}
                for key, value in normalized_components.items():
                    merged_components[key] = value
                snapshot = EntitySnapshot(
                    entity_id=entity_id,
                    object_type=object_type,
                    provenance=provenance,
                    expires_at=expires_at,
                    components=merged_components,
                    updated_at=now,
                )
            self._entities[entity_id] = snapshot
        await self._broadcast(snapshot)
        ttl_metadata: dict[str, Any] = {"ttl_seconds": ttl.total_seconds()}
        if metadata:
            ttl_metadata.update(metadata)
        await self._record_event(
            "upsert",
            snapshot,
            metadata=ttl_metadata,
        )
        return snapshot

    async def remove(self, entity_id: str, *, metadata: Mapping[str, Any] | None = None) -> None:
        """Remove an entity and publish a tombstone event."""

        async with self._lock:
            snapshot = self._entities.pop(entity_id, None)
            if snapshot is None:
                return
        tombstone = EntitySnapshot(
            entity_id=entity_id,
            object_type=snapshot.object_type,
            provenance=snapshot.provenance,
            expires_at=datetime.now(UTC),
            components={},
            updated_at=datetime.now(UTC),
        )
        await self._broadcast(tombstone)
        event_metadata = {"reason": "explicit"}
        if metadata:
            event_metadata.update(metadata)
        await self._record_event(
            "remove",
            tombstone,
            metadata=event_metadata,
        )

    async def list_entities(self) -> list[EntitySnapshot]:
        async with self._lock:
            return [snapshot for snapshot in self._entities.values()]

    async def get_entity(self, entity_id: str) -> EntitySnapshot | None:
        async with self._lock:
            return self._entities.get(entity_id)

    async def prune_expired(self) -> int:
        """Remove expired entities and notify subscribers. Returns number pruned."""

        now = datetime.now(UTC)
        async with self._lock:
            expired_entries = [
                (entity_id, snapshot)
                for entity_id, snapshot in list(self._entities.items())
                if snapshot.is_expired(at=now)
            ]
            for entity_id, _ in expired_entries:
                del self._entities[entity_id]
        for entity_id, expired_snapshot in expired_entries:
            tombstone = EntitySnapshot(
                entity_id=entity_id,
                object_type=expired_snapshot.object_type,
                provenance="system",
                expires_at=now,
                components={},
                updated_at=now,
            )
            await self._broadcast(tombstone)
            await self._record_event(
                "expire",
                tombstone,
                metadata={"reason": "ttl"},
            )
        return len(expired_entries)

    async def apply_component_patch(
        self,
        entity_id: str,
        *,
        components: Mapping[str, Mapping[str, Any]],
        provenance: str | None = None,
        ttl: timedelta | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> EntitySnapshot | None:
        """Merge additional components into an existing entity."""

        normalized_components: dict[str, dict[str, Any]]
        async with self._lock:
            snapshot = self._entities.get(entity_id)
            if snapshot is None:
                return None
            normalized_components = self._normalize_components(snapshot.object_type, components)
            merged_components = {key: dict(value) for key, value in snapshot.components.items()}
            changed = False
            for name, payload in normalized_components.items():
                if merged_components.get(name) != payload:
                    merged_components[name] = payload
                    changed = True

            new_expires_at = snapshot.expires_at
            if ttl is not None:
                if ttl.total_seconds() <= 0:
                    raise ValueError("TTL must be positive")
                new_expires_at = datetime.now(UTC) + ttl

            new_provenance = provenance or snapshot.provenance
            if (
                not changed
                and new_expires_at == snapshot.expires_at
                and new_provenance == snapshot.provenance
            ):
                return snapshot

            updated_snapshot = EntitySnapshot(
                entity_id=snapshot.entity_id,
                object_type=snapshot.object_type,
                provenance=new_provenance,
                expires_at=new_expires_at,
                components=merged_components,
                updated_at=datetime.now(UTC),
            )
            self._entities[entity_id] = updated_snapshot

        await self._broadcast(updated_snapshot)
        await self._record_event("patch", updated_snapshot, metadata=dict(metadata or {}))
        return updated_snapshot

    async def load_snapshots(self, snapshots: Iterable[EntitySnapshot]) -> None:
        async with self._lock:
            self._entities = {snapshot.entity_id: snapshot for snapshot in snapshots}

    def subscribe(
        self, *, object_types: set[str] | None = None
    ) -> tuple[int, asyncio.Queue[EntitySnapshot | None]]:
        queue: asyncio.Queue[EntitySnapshot | None] = asyncio.Queue(
            maxsize=self._subscriber_queue_size
        )
        subscriber_id = next(self._id_counter)
        self._subscribers[subscriber_id] = (queue, object_types)
        return subscriber_id, queue

    def unsubscribe(self, subscriber_id: int) -> None:
        subscriber = self._subscribers.pop(subscriber_id, None)
        if subscriber is None:
            return
        queue, _ = subscriber
        try:
            queue.put_nowait(None)
        except asyncio.QueueFull:
            self._drain_queue(queue)
            queue.put_nowait(None)

    async def _broadcast(self, snapshot: EntitySnapshot) -> None:
        dead_subscribers: list[int] = []
        for subscriber_id, (queue, object_types) in self._subscribers.items():
            if object_types and snapshot.object_type and snapshot.object_type not in object_types:
                continue
            try:
                queue.put_nowait(snapshot)
            except asyncio.QueueFull:
                dead_subscribers.append(subscriber_id)
        for subscriber_id in dead_subscribers:
            subscriber = self._subscribers.pop(subscriber_id, None)
            if subscriber is None:
                continue
            queue, _ = subscriber
            self._drain_queue(queue)
            queue.put_nowait(None)

    @staticmethod
    def _drain_queue(queue: asyncio.Queue[EntitySnapshot | None]) -> None:
        while not queue.empty():
            try:
                queue.get_nowait()
            except QueueEmpty:  # pragma: no cover - race condition safe-guard
                break

    def _normalize_components(
        self, object_type: str, components: Mapping[str, Mapping[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        if self._schema_registry is None:
            return {key: dict(value) for key, value in components.items()}
        return self._schema_registry.normalize_components(object_type, components)

    async def _record_event(
        self,
        event_type: str,
        snapshot: EntitySnapshot,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        if self._journal is None:
            return
        metadata_payload = dict(metadata or {})
        event = EntityEvent(
            sequence=next(self._event_counter),
            event_type=event_type,
            entity_id=snapshot.entity_id,
            object_type=snapshot.object_type,
            provenance=snapshot.provenance,
            components={key: dict(value) for key, value in snapshot.components.items()},
            expires_at=snapshot.expires_at,
            updated_at=snapshot.updated_at,
            metadata=metadata_payload,
        )
        try:
            await self._journal.record(event)
        except Exception:  # pragma: no cover - journaling errors should not break flow
            logger.exception(
                "Failed to record %s event for entity %s", event_type, snapshot.entity_id
            )
