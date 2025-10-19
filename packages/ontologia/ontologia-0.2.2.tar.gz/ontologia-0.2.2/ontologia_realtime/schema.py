from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import timedelta
from threading import RLock
from typing import Any

ComponentNormalizer = Callable[[Mapping[str, Any]], Mapping[str, Any]]


def _copy_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items()}


@dataclass(slots=True, frozen=True)
class ComponentSchema:
    normalizer: ComponentNormalizer = field(default=_copy_payload)
    required: bool = field(default=False)

    def normalize(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        normalized = self.normalizer(payload)
        if not isinstance(normalized, Mapping):
            raise TypeError("Component normalizer must return a mapping")
        return {key: value for key, value in normalized.items()}


@dataclass(slots=True, frozen=True)
class EntitySchema:
    object_type: str
    default_ttl: timedelta | None = None
    components: dict[str, ComponentSchema] = field(default_factory=dict)


class SchemaRegistry:
    def __init__(self) -> None:
        self._schemas: dict[str, EntitySchema] = {}
        self._lock = RLock()

    def register(
        self,
        object_type: str,
        *,
        default_ttl: timedelta | None = None,
        components: Mapping[str, ComponentSchema | ComponentNormalizer] | None = None,
    ) -> None:
        component_schemas: dict[str, ComponentSchema] = {}
        if components:
            for name, spec in components.items():
                if isinstance(spec, ComponentSchema):
                    component_schemas[name] = spec
                    continue
                if not callable(spec):
                    raise TypeError(
                        f"Component spec for '{name}' must be callable or ComponentSchema"
                    )
                component_schemas[name] = ComponentSchema(normalizer=spec)
        schema = EntitySchema(
            object_type=object_type,
            default_ttl=default_ttl,
            components=component_schemas,
        )
        with self._lock:
            self._schemas[object_type] = schema

    def get(self, object_type: str) -> EntitySchema | None:
        with self._lock:
            return self._schemas.get(object_type)

    def normalize_components(
        self, object_type: str, components: Mapping[str, Mapping[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        schema = self.get(object_type)
        if schema is None:
            return {name: _copy_payload(payload) for name, payload in components.items()}
        normalized: dict[str, dict[str, Any]] = {}
        for name, payload in components.items():
            component_schema = schema.components.get(name)
            if component_schema is None:
                normalized[name] = _copy_payload(payload)
                continue
            normalized[name] = component_schema.normalize(payload)
        missing_required = [
            name
            for name, component_schema in schema.components.items()
            if component_schema.required and name not in normalized
        ]
        if missing_required:
            raise ValueError(
                f"Missing required components for '{object_type}': {', '.join(sorted(missing_required))}"
            )
        return normalized

    def resolve_ttl(self, object_type: str, ttl: timedelta | None) -> timedelta | None:
        if ttl is not None:
            return ttl
        schema = self.get(object_type)
        return schema.default_ttl if schema else None


__all__ = [
    "ComponentSchema",
    "EntitySchema",
    "SchemaRegistry",
]
