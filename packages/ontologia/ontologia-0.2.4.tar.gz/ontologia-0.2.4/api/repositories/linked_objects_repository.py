"""Backward-compatible import for SQL repositories."""

from __future__ import annotations

from ontologia.infrastructure.persistence.sql.linked_objects_repository import (
    SQLLinkRepository as LinkedObjectsRepository,
)

__all__ = ["LinkedObjectsRepository"]
