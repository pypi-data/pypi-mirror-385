"""Domain events for metamodel changes."""

from __future__ import annotations

from dataclasses import dataclass

from ontologia.domain.events import DomainEvent


@dataclass(frozen=True, slots=True)
class ObjectTypeCreated(DomainEvent):
    service: str
    instance: str
    object_type_api_name: str
    version: int


@dataclass(frozen=True, slots=True)
class ObjectTypeUpdated(DomainEvent):
    service: str
    instance: str
    object_type_api_name: str
    from_version: int
    to_version: int
