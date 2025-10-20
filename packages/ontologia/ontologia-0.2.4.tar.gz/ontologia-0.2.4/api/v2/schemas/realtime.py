"""Schemas for hybrid real-time entity responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HybridEntityResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    entityId: str = Field(..., description="Entity identifier in the real-time layer")
    objectType: str = Field(..., description="Ontologia ObjectType backing the entity")
    provenance: str = Field(..., description="Source of the latest update")
    expiresAt: datetime = Field(..., description="Expiration timestamp")
    updatedAt: datetime = Field(..., description="Last update timestamp")
    components: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Merged components including real-time payload and enrichment",
    )
    historical: dict[str, Any] | None = Field(
        default=None,
        description="Historical context fetched from the analytical store",
    )


class RealtimeEventResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sequence: int = Field(..., description="Monotonic sequence captured in the journal")
    eventType: str = Field(..., description="Type of the event: upsert, patch, remove, expire")
    entityId: str = Field(..., description="Entity identifier in the real-time layer")
    objectType: str = Field(..., description="Ontologia ObjectType involved")
    provenance: str = Field(..., description="Source of the event")
    updatedAt: datetime = Field(..., description="Timestamp captured when the event was recorded")
    expiresAt: datetime = Field(..., description="Expiry timestamp associated with the entity")
    components: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Component payload associated with the event",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata emitted alongside the event",
    )
