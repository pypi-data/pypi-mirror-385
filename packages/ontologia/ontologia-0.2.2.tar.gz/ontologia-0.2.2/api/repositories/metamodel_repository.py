"""Backward-compatible import for SQL repositories."""

from __future__ import annotations

from ontologia.infrastructure.persistence.sql.metamodel_repository import (
    SQLMetamodelRepository as MetamodelRepository,
)

__all__ = ["MetamodelRepository"]
