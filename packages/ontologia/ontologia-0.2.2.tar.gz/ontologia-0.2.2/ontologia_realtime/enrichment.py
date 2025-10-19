from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from typing import Protocol

from ontologia_realtime.entity_manager import EntityManager, EntitySnapshot

logger = logging.getLogger(__name__)


class ContextProvider(Protocol):
    """Fetches historical context to enrich an entity snapshot."""

    async def fetch(
        self, snapshot: EntitySnapshot
    ) -> Mapping[str, Mapping[str, object]]:  # pragma: no cover - interface
        ...


class RealTimeEnricher:
    """Bridges the hot state with historical context by patching missing components."""

    def __init__(
        self,
        manager: EntityManager,
        provider: ContextProvider,
        *,
        provenance: str = "enrichment",
        object_types: set[str] | None = None,
        poll_timeout: float = 0.5,
    ) -> None:
        self._manager = manager
        self._provider = provider
        self._provenance = provenance
        self._object_types = object_types
        self._poll_timeout = poll_timeout

    async def run(self, stop_event: asyncio.Event | None = None) -> None:
        """Continuously consumes entity updates and enriches them."""

        subscriber_id, queue = self._manager.subscribe(object_types=self._object_types)
        try:
            while True:
                if stop_event and stop_event.is_set():
                    break
                try:
                    snapshot = await asyncio.wait_for(
                        queue.get(), timeout=self._poll_timeout if stop_event else None
                    )
                except TimeoutError:
                    continue

                if snapshot is None:
                    break
                if snapshot.provenance == self._provenance:
                    continue

                try:
                    context = await self._provider.fetch(snapshot)
                except Exception:  # pragma: no cover - provider issues should not kill loop
                    logger.exception(
                        "Failed to fetch enrichment context",
                        extra={
                            "entity_id": snapshot.entity_id,
                            "object_type": snapshot.object_type,
                        },
                    )
                    continue

                if not context:
                    continue

                existing = snapshot.components
                diff = {
                    name: dict(payload)
                    for name, payload in context.items()
                    if existing.get(name) != dict(payload)
                }
                if not diff:
                    continue

                metadata = {"enriched_components": sorted(diff)}
                await self._manager.apply_component_patch(
                    snapshot.entity_id,
                    components=diff,
                    provenance=self._provenance,
                    metadata=metadata,
                )
        finally:
            self._manager.unsubscribe(subscriber_id)


__all__ = ["ContextProvider", "RealTimeEnricher"]
