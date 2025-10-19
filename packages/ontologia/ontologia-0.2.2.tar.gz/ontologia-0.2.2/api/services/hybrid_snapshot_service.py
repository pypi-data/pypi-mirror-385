from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from api.services.instances_service import InstancesService
from ontologia_realtime.entity_manager import EntityManager


@dataclass(slots=True)
class HybridEntityView:
    entity_id: str
    object_type: str
    provenance: str
    expires_at: datetime
    updated_at: datetime
    components: dict[str, dict[str, Any]]
    historical: dict[str, Any] | None


class HybridSnapshotService:
    """Combines the hot EntityManager state with cold historical context."""

    def __init__(
        self,
        manager: EntityManager,
        instances_service: InstancesService,
        *,
        historical_component: str = "historical",
    ) -> None:
        self._manager = manager
        self._instances_service = instances_service
        self._historical_component = historical_component

    async def get_entity(self, entity_id: str) -> HybridEntityView | None:
        snapshot = await self._manager.get_entity(entity_id)
        if snapshot is None:
            return None

        historical = await asyncio.to_thread(
            self._instances_service.get_object,
            snapshot.object_type,
            entity_id,
        )

        components = {key: dict(value) for key, value in snapshot.components.items()}
        historical_payload = dict(historical.properties or {}) if historical else None
        if historical_payload:
            components.setdefault(self._historical_component, historical_payload)

        return HybridEntityView(
            entity_id=snapshot.entity_id,
            object_type=snapshot.object_type,
            provenance=snapshot.provenance,
            expires_at=snapshot.expires_at,
            updated_at=snapshot.updated_at,
            components=components,
            historical=historical_payload,
        )
