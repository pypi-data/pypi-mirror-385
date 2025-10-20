"""Backward-compatible import for SQL repositories."""

from __future__ import annotations

from ontologia.infrastructure.persistence.sql.instances_repository import (
    SQLObjectInstanceRepository as InstancesRepository,
)

__all__ = ["InstancesRepository"]
