"""Models for schema migration orchestration tasks."""

from __future__ import annotations

from enum import Enum
from typing import Any

from registro import ResourceTypeBaseModel
from sqlmodel import JSON, Column, Field


class MigrationTaskStatus(str, Enum):
    """Status lifecycle for schema migration tasks."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MigrationTask(ResourceTypeBaseModel, table=True):
    """Represents a schema migration task generated for destructive changes."""

    __resource_type__ = "migration-task"
    __tablename__ = "migrationtask"

    object_type_api_name: str = Field(index=True)
    from_version: int = Field(..., ge=1)
    to_version: int = Field(..., ge=1)
    plan: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    status: MigrationTaskStatus = Field(default=MigrationTaskStatus.PENDING)
    error_message: str | None = Field(default=None)


MigrationTask.model_rebuild()
