"""Value objects used within the metamodel domain layer."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, replace
from typing import Any


@dataclass(frozen=True, slots=True)
class PrimaryKeyDefinition:
    """Represents the primary key contract for an :class:`ObjectType`."""

    name: str

    def ensure_present(self, properties: PropertySet) -> None:
        if self.name not in properties:
            raise ValueError(f"Primary key '{self.name}' must exist in property set")
        properties.promote_to_primary_key(self.name)


@dataclass(frozen=True, slots=True)
class PropertyDefinition:
    """Immutable description of a property belonging to an object or link aggregate."""

    api_name: str
    data_type: str
    display_name: str | None = None
    description: str | None = None
    required: bool = False
    quality_checks: tuple[str, ...] = ()
    data_type_config: dict[str, Any] | None = None
    derivation_script: str | None = None
    references_object_type_api_name: str | None = None
    is_primary_key: bool = False

    def as_primary_key(self) -> PropertyDefinition:
        return replace(self, required=True, is_primary_key=True)

    def ensure_identifier(self) -> None:
        if not self.api_name.isidentifier():
            raise ValueError(f"Property '{self.api_name}' must be a valid identifier")


class PropertySet:
    """Collection helper that enforces uniqueness and exposes lookup utilities."""

    def __init__(self, properties: Iterable[PropertyDefinition]):
        props = list(properties)
        self._properties = {prop.api_name: prop for prop in props}
        if len(self._properties) != len(props):
            raise ValueError("Duplicate property api_name detected")
        for prop in self._properties.values():
            prop.ensure_identifier()

    def __contains__(self, api_name: str) -> bool:
        return api_name in self._properties

    def __iter__(self) -> Iterator[PropertyDefinition]:
        return iter(self._properties.values())

    def __len__(self) -> int:
        return len(self._properties)

    def __getitem__(self, api_name: str) -> PropertyDefinition:
        try:
            return self._properties[api_name]
        except KeyError as exc:
            raise ValueError(f"Property '{api_name}' not found") from exc

    def get(self, api_name: str) -> PropertyDefinition | None:
        return self._properties.get(api_name)

    def add(self, prop: PropertyDefinition) -> None:
        prop.ensure_identifier()
        if prop.api_name in self._properties:
            raise ValueError(f"Property '{prop.api_name}' already exists")
        self._properties[prop.api_name] = prop

    def replace(self, prop: PropertyDefinition) -> None:
        prop.ensure_identifier()
        self._properties[prop.api_name] = prop

    def remove(self, api_name: str) -> None:
        try:
            del self._properties[api_name]
        except KeyError as exc:
            raise ValueError(f"Property '{api_name}' not found") from exc

    def promote_to_primary_key(self, api_name: str) -> None:
        current = self._properties.get(api_name)
        if current is None:
            raise ValueError(f"Property '{api_name}' not found")
        self._properties[api_name] = current.as_primary_key()

    def enforce_required(self, api_name: str) -> None:
        current = self._properties.get(api_name)
        if current is None:
            raise ValueError(f"Property '{api_name}' not found")
        self._properties[api_name] = replace(current, required=True)

    def values(self) -> list[PropertyDefinition]:
        return list(self._properties.values())

    def primary_keys(self) -> list[PropertyDefinition]:
        return [prop for prop in self._properties.values() if prop.is_primary_key]
