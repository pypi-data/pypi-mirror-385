"""Domain events for runtime instance mutations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ontologia.domain.events import DomainEvent


@dataclass(frozen=True, slots=True)
class ObjectInstanceUpserted(DomainEvent):
    service: str
    instance: str
    object_type_api_name: str
    primary_key_field: str
    primary_key_value: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ObjectInstanceDeleted(DomainEvent):
    service: str
    instance: str
    object_type_api_name: str
    primary_key_field: str
    primary_key_value: str


@dataclass(frozen=True, slots=True)
class LinkCreated(DomainEvent):
    service: str
    instance: str
    link_type_api_name: str
    from_object_type: str
    to_object_type: str
    from_primary_key_field: str
    to_primary_key_field: str
    from_pk: str
    to_pk: str
    properties: dict[str, Any] = field(default_factory=dict)
    property_names: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LinkDeleted(DomainEvent):
    service: str
    instance: str
    link_type_api_name: str
    from_object_type: str
    to_object_type: str
    from_primary_key_field: str
    to_primary_key_field: str
    from_pk: str
    to_pk: str
