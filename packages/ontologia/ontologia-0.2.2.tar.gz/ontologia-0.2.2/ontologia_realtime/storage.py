from __future__ import annotations

import asyncio
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from ontologia_realtime.entity_manager import EntitySnapshot
from ontologia_realtime.journal import EntityEvent


class EntityStore(Protocol):
    async def load_snapshots(self) -> list[EntitySnapshot]:  # pragma: no cover - interface
        ...

    async def apply_event(self, event: EntityEvent) -> None:  # pragma: no cover - interface
        ...


@dataclass(slots=True)
class SQLiteEntityStore(EntityStore):
    path: Path

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(
            self.path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False
        )

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    entity_id TEXT PRIMARY KEY,
                    object_type TEXT NOT NULL,
                    provenance TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    components TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_entities_updated_at
                ON entities(updated_at)
                """
            )
            conn.commit()

    async def load_snapshots(self) -> list[EntitySnapshot]:
        return await asyncio.to_thread(self._load_snapshots_sync)

    def _load_snapshots_sync(self) -> list[EntitySnapshot]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT entity_id, object_type, provenance, expires_at, updated_at, components FROM entities"
            )
            rows = cursor.fetchall()
        snapshots: list[EntitySnapshot] = []
        for entity_id, object_type, provenance, expires_at, updated_at, components_json in rows:
            components = json.loads(components_json)
            expires_dt = datetime.fromisoformat(expires_at)
            if expires_dt.tzinfo is None:
                expires_dt = expires_dt.replace(tzinfo=UTC)
            else:
                expires_dt = expires_dt.astimezone(UTC)
            updated_dt = datetime.fromisoformat(updated_at)
            if updated_dt.tzinfo is None:
                updated_dt = updated_dt.replace(tzinfo=UTC)
            else:
                updated_dt = updated_dt.astimezone(UTC)
            snapshots.append(
                EntitySnapshot(
                    entity_id=entity_id,
                    object_type=object_type,
                    provenance=provenance,
                    expires_at=expires_dt,
                    components=components,
                    updated_at=updated_dt,
                )
            )
        return snapshots

    async def apply_event(self, event: EntityEvent) -> None:
        await asyncio.to_thread(self._apply_event_sync, event)

    def _apply_event_sync(self, event: EntityEvent) -> None:
        if event.event_type in {"remove", "expire"}:
            self._delete_entity(event.entity_id)
            return
        self._upsert_entity(event)

    def _upsert_entity(self, event: EntityEvent) -> None:
        payload = json.dumps(event.components)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO entities (entity_id, object_type, provenance, expires_at, updated_at, components)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(entity_id) DO UPDATE SET
                    object_type=excluded.object_type,
                    provenance=excluded.provenance,
                    expires_at=excluded.expires_at,
                    updated_at=excluded.updated_at,
                    components=excluded.components
                """,
                (
                    event.entity_id,
                    event.object_type,
                    event.provenance,
                    event.expires_at.isoformat(),
                    event.updated_at.isoformat(),
                    payload,
                ),
            )
            conn.commit()

    def _delete_entity(self, entity_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM entities WHERE entity_id = ?", (entity_id,))
            conn.commit()


__all__ = ["EntityStore", "SQLiteEntityStore"]
