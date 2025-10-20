"""SQLModel models for change set workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import field_validator
from registro import ResourceTypeBaseModel
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import JSON, Column, Field


class ChangeSet(ResourceTypeBaseModel, table=True):
    __resource_type__ = "change-set"
    __tablename__ = "changeset"

    dataset_rid: str = Field(foreign_key="dataset.rid", index=True)
    name: str = Field(index=True)
    status: str = Field(default="pending", index=True)
    target_object_type: str = Field(index=True)
    base_branch: str | None = Field(default=None)
    description: str | None = Field(default=None)
    created_by: str | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    approved_at: datetime | None = Field(default=None)
    payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(MutableDict.as_mutable(JSON)),
    )

    @field_validator("approved_at", mode="before")
    @classmethod
    def _ensure_approved_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value

    @classmethod
    def generate_api_name(cls, name: str) -> str:
        suffix = uuid4().hex[:8]
        base = name.lower().replace(" ", "-")[:40]
        return f"changeset-{base}-{suffix}"
