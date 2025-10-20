"""Aggregate root for object type domain operations."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.domain.metamodels.types.property_type import PropertyType

from ..value_objects import PrimaryKeyDefinition, PropertyDefinition, PropertySet


@dataclass(slots=True)
class ObjectTypeAggregate:
    """Aggregate root enforcing invariants for :class:`ObjectType`."""

    object_type: ObjectType
    properties: PropertySet
    primary_key: PrimaryKeyDefinition
    _models: dict[str, PropertyType] = field(default_factory=dict, init=False, repr=False)

    @classmethod
    def new(
        cls,
        *,
        object_type: ObjectType,
        properties: Iterable[PropertyDefinition],
        primary_key: PrimaryKeyDefinition,
    ) -> ObjectTypeAggregate:
        prop_set = PropertySet(properties)
        primary_key.ensure_present(prop_set)
        aggregate = cls(object_type=object_type, properties=prop_set, primary_key=primary_key)
        aggregate._models = {}
        aggregate._synchronize_models()
        aggregate._validate_invariants()
        return aggregate

    @classmethod
    def from_model(cls, object_type: ObjectType) -> ObjectTypeAggregate:
        props: list[PropertyDefinition] = [
            PropertyDefinition(
                api_name=p.api_name,
                data_type=p.data_type,
                display_name=p.display_name,
                description=p.description,
                required=p.required,
                quality_checks=tuple(p.quality_checks or []),
                data_type_config=dict(p.data_type_config or {}),
                derivation_script=p.derivation_script,
                references_object_type_api_name=p.references_object_type_api_name,
                is_primary_key=bool(p.is_primary_key),
            )
            for p in getattr(object_type, "property_types", []) or []
        ]
        prop_set = PropertySet(props)
        pk = PrimaryKeyDefinition(object_type.primary_key_field)
        pk.ensure_present(prop_set)
        aggregate = cls(object_type=object_type, properties=prop_set, primary_key=pk)
        aggregate._models = {
            p.api_name: p for p in getattr(object_type, "property_types", []) or []
        }
        aggregate._synchronize_models()
        aggregate._validate_invariants()
        return aggregate

    def define_primary_key(self, api_name: str) -> None:
        self.primary_key = PrimaryKeyDefinition(api_name)
        self.primary_key.ensure_present(self.properties)
        self.object_type.primary_key_field = api_name
        self._synchronize_models()
        self._validate_invariants()

    def add_property(self, definition: PropertyDefinition) -> None:
        self.properties.add(definition)
        if definition.is_primary_key:
            self.primary_key = PrimaryKeyDefinition(definition.api_name)
        self._synchronize_models()
        self._validate_invariants()

    def remove_property(self, api_name: str) -> None:
        if api_name == self.primary_key.name:
            raise ValueError("Cannot remove primary key property")
        self.properties.remove(api_name)
        self._models.pop(api_name, None)
        self._synchronize_models()
        self._validate_invariants()

    def update_property(self, definition: PropertyDefinition) -> None:
        if definition.api_name == self.primary_key.name and not definition.is_primary_key:
            definition = definition.as_primary_key()
        self.properties.replace(definition)
        if definition.is_primary_key:
            self.primary_key = PrimaryKeyDefinition(definition.api_name)
        self._synchronize_models()
        self._validate_invariants()

    def normalize_instance_properties(
        self, pk_value: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        data = dict(payload or {})
        data[self.primary_key.name] = pk_value
        known = {prop.api_name for prop in self.properties}
        unknown = [name for name in data.keys() if name not in known]
        if unknown:
            raise ValueError(f"Unknown properties for '{self.object_type.api_name}': {unknown}")

        required = [
            prop.api_name for prop in self.properties if prop.required or prop.is_primary_key
        ]
        missing = [name for name in required if data.get(name) is None]
        if missing:
            raise ValueError(
                f"Missing required properties for '{self.object_type.api_name}': {missing}"
            )

        normalized: dict[str, Any] = {}
        for prop in self.properties:
            if prop.api_name not in data:
                continue
            normalized[prop.api_name] = self._coerce_value(data[prop.api_name], prop.data_type)
        return normalized

    def _validate_invariants(self) -> None:
        primary_keys = self.properties.primary_keys()
        if not primary_keys:
            raise ValueError("ObjectType aggregate must have a primary key")
        if len(primary_keys) > 1:
            raise ValueError("ObjectType aggregate cannot have multiple primary keys")
        if primary_keys[0].api_name != self.primary_key.name:
            raise ValueError("Primary key property mismatch")
        for prop in self.properties:
            if (
                prop.references_object_type_api_name
                and not prop.references_object_type_api_name.isidentifier()
            ):
                raise ValueError(
                    f"Property '{prop.api_name}' references invalid object type identifier"
                )

    def _synchronize_models(self) -> None:
        model_props: list[PropertyType] = []
        for prop in self.properties:
            model_props.append(self._ensure_model(prop))
        self.object_type.property_types = model_props
        self.object_type.primary_key_field = self.primary_key.name

    def _ensure_model(self, prop: PropertyDefinition) -> PropertyType:
        existing = self._models.get(prop.api_name)
        if existing is None:
            existing = PropertyType(
                service=self.object_type.service,
                instance=self.object_type.instance,
                api_name=prop.api_name,
                display_name=prop.display_name or prop.api_name,
                description=prop.description,
                data_type=prop.data_type,
                data_type_config=dict(prop.data_type_config or {}),
                quality_checks=list(prop.quality_checks),
                is_primary_key=prop.is_primary_key,
                required=prop.required or prop.is_primary_key,
                derivation_script=prop.derivation_script,
                references_object_type_api_name=prop.references_object_type_api_name,
                object_type_rid=self.object_type.rid,
                object_type_api_name=self.object_type.api_name,
            )
            self._models[prop.api_name] = existing
            return existing
        existing.display_name = prop.display_name or prop.api_name
        existing.description = prop.description
        existing.data_type = prop.data_type
        existing.data_type_config = dict(prop.data_type_config or {})
        existing.quality_checks = list(prop.quality_checks)
        existing.is_primary_key = prop.is_primary_key
        existing.required = prop.required or prop.is_primary_key
        existing.derivation_script = prop.derivation_script
        existing.references_object_type_api_name = prop.references_object_type_api_name
        existing.object_type_rid = self.object_type.rid
        existing.object_type_api_name = self.object_type.api_name
        return existing

    @staticmethod
    def _coerce_value(value: Any, data_type: str) -> Any:
        if value is None:
            return None
        dt = (data_type or "string").lower()
        if dt == "string":
            return str(value)
        error_msg = f"Invalid value '{value}' for type '{data_type}'"
        if dt in {"integer", "int", "long"}:
            if isinstance(value, bool):
                raise ValueError(error_msg)
            if isinstance(value, int):
                return value
            if isinstance(value, float) and value.is_integer():
                return int(value)
            if isinstance(value, str):
                try:
                    return int(value)
                except Exception as exc:
                    raise ValueError(error_msg) from exc
            raise ValueError(error_msg)
        if dt in {"double", "float"}:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value)
                except Exception as exc:
                    raise ValueError(error_msg) from exc
            raise ValueError(error_msg)
        if dt in {"boolean", "bool"}:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in {"true", "1", "yes"}:
                    return True
                if lowered in {"false", "0", "no"}:
                    return False
            raise ValueError(error_msg)
        if dt in {"date", "timestamp"}:
            return str(value)
        return value
