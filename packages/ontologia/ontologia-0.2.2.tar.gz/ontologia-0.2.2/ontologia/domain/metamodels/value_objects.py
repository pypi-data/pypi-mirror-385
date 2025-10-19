"""Backward-compatible exports for legacy import paths."""

from __future__ import annotations

from ontologia.domain.metamodel.value_objects import (  # noqa: F401
    PrimaryKeyDefinition,
    PropertyDefinition,
    PropertySet,
)

__all__ = ["PrimaryKeyDefinition", "PropertyDefinition", "PropertySet"]
