"""Metamodel domain package organized by bounded context."""

from __future__ import annotations

from . import events, repositories, value_objects

__all__ = [
    "events",
    "repositories",
    "value_objects",
]
