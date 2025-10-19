from __future__ import annotations

import logging

from api.repositories.kuzudb_repository import get_kuzu_repo
from ontologia.config import use_graph_writes_enabled
from ontologia.domain.events import (
    InProcessEventBus,
    LinkCreated,
    LinkDeleted,
    ObjectInstanceDeleted,
    ObjectInstanceUpserted,
)

logger = logging.getLogger(__name__)
_registered_buses: set[int] = set()


class GraphEventHandler:
    def __init__(self) -> None:
        self._kuzu_repo = get_kuzu_repo()

    def handle_object_instance_upserted(self, event: ObjectInstanceUpserted) -> None:
        if not self._should_write():
            return
        if not event.primary_key_field:
            return
        props = dict(event.payload or {})
        set_parts: list[str] = []
        create_parts: list[str] = []
        for key, value in props.items():
            if value is None:
                continue
            literal = self._kuzu_literal(value)
            set_parts.append(f"o.{key} = {literal}")
            create_parts.append(f"{key}: {literal}")
        if not set_parts or not create_parts:
            return
        pk_literal = self._kuzu_literal(event.primary_key_value)
        label = event.object_type_api_name
        pk_field = event.primary_key_field
        update_query = (
            f"MATCH (o:`{label}`) WHERE o.`{pk_field}` = {pk_literal} "
            f"SET {', '.join(set_parts)}"
        )
        create_query = f"CREATE (:{label} {{{', '.join(create_parts)}}})"
        self._execute(update_query)
        try:
            self._execute(create_query)
        except Exception:
            logger.debug("graph node insert failed, likely already exists", exc_info=True)

    def handle_object_instance_deleted(self, event: ObjectInstanceDeleted) -> None:
        if not self._should_write():
            return
        if not event.primary_key_field:
            return
        pk_literal = self._kuzu_literal(event.primary_key_value)
        label = event.object_type_api_name
        pk_field = event.primary_key_field
        query = f"MATCH (o:`{label}`) WHERE o.`{pk_field}` = {pk_literal} DELETE o"
        self._execute(query)

    def handle_link_created(self, event: LinkCreated) -> None:
        if not self._should_write():
            return
        if not event.from_primary_key_field or not event.to_primary_key_field:
            return
        from_literal = self._kuzu_literal(event.from_pk)
        to_literal = self._kuzu_literal(event.to_pk)
        base_match = (
            f"MATCH (a:`{event.from_object_type}`), (b:`{event.to_object_type}`) "
            f"WHERE a.`{event.from_primary_key_field}` = {from_literal} "
            f"AND b.`{event.to_primary_key_field}` = {to_literal} "
            f"CREATE (a)-[r:`{event.link_type_api_name}`]->(b)"
        )
        props = event.properties or {}
        allowed_names = event.property_names or tuple(props.keys())
        set_parts = [
            f"r.{name} = {self._kuzu_literal(props[name])}"
            for name in allowed_names
            if name in props and props[name] is not None
        ]
        if set_parts:
            base_match += f" SET {', '.join(set_parts)}"
        self._execute(base_match)

    def handle_link_deleted(self, event: LinkDeleted) -> None:
        if not self._should_write():
            return
        if not event.from_primary_key_field or not event.to_primary_key_field:
            return
        from_literal = self._kuzu_literal(event.from_pk)
        to_literal = self._kuzu_literal(event.to_pk)
        query = (
            f"MATCH (a:`{event.from_object_type}`)-[r:`{event.link_type_api_name}`]->"
            f"(b:`{event.to_object_type}`) WHERE a.`{event.from_primary_key_field}` = {from_literal} "
            f"AND b.`{event.to_primary_key_field}` = {to_literal} DELETE r"
        )
        self._execute(query)

    def _should_write(self) -> bool:
        if not use_graph_writes_enabled():
            return False
        try:
            return bool(self._kuzu_repo and self._kuzu_repo.is_available())
        except Exception:
            return False

    def _execute(self, query: str) -> None:
        if not query:
            return
        try:
            self._kuzu_repo.execute(query)  # type: ignore[union-attr]
        except Exception:
            logger.debug("graph sync query failed: %s", query, exc_info=True)

    @staticmethod
    def _kuzu_literal(value: object) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"


def register_graph_event_handlers(bus: InProcessEventBus) -> None:
    if not isinstance(bus, InProcessEventBus):
        return
    key = id(bus)
    if key in _registered_buses:
        return
    handler = GraphEventHandler()
    bus.subscribe(ObjectInstanceUpserted, handler.handle_object_instance_upserted)
    bus.subscribe(ObjectInstanceDeleted, handler.handle_object_instance_deleted)
    bus.subscribe(LinkCreated, handler.handle_link_created)
    bus.subscribe(LinkDeleted, handler.handle_link_deleted)
    _registered_buses.add(key)
