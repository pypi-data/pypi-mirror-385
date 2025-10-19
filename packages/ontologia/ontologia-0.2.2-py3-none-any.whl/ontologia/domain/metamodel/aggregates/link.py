"""Aggregate logic for link instances."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ontologia.domain.metamodels.instances.models_sql import LinkedObject, ObjectInstance
from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType


@dataclass(slots=True)
class LinkAggregate:
    """Aggregate representing a single link edge between two object instances."""

    link_type: LinkType
    from_instance: ObjectInstance
    to_instance: ObjectInstance
    properties: dict[str, Any] = field(default_factory=dict)

    def validate_cardinality(self, forward_degree: int, inverse_degree: int) -> None:
        forward, inverse = self._side_cardinalities()
        if forward == "ONE" and forward_degree > 0:
            raise ValueError(
                f"Cardinality violation: '{self.link_type.api_name}' forward is ONE for "
                f"'{self.link_type.from_object_type_api_name}'"
            )
        if inverse == "ONE" and inverse_degree > 0:
            raise ValueError(
                f"Cardinality violation: '{self.link_type.api_name}' inverse is ONE for "
                f"'{self.link_type.to_object_type_api_name}'"
            )

    def validate_properties(self) -> None:
        allowed = {
            prop.api_name for prop in (getattr(self.link_type, "link_property_types", []) or [])
        }
        if not allowed:
            return
        invalid = [key for key in self.properties.keys() if key not in allowed]
        if invalid:
            raise ValueError(
                f"Unknown link properties for '{self.link_type.api_name}': {sorted(invalid)}"
            )

    def build_model(self, *, service: str, instance: str) -> LinkedObject:
        return LinkedObject(
            service=service,
            instance=instance,
            api_name=self.identifier,
            display_name=f"{self.link_type.api_name} {self.from_instance.pk_value}→{self.to_instance.pk_value}",
            link_type_api_name=self.link_type.api_name,
            link_type_rid=self.link_type.rid,
            from_object_rid=self.from_instance.rid,
            to_object_rid=self.to_instance.rid,
            data=dict(self.properties or {}),
        )

    @property
    def identifier(self) -> str:
        return (
            f"{self.link_type.api_name}:{self.from_instance.pk_value}->{self.to_instance.pk_value}"
        )

    def _side_cardinalities(self) -> tuple[str, str]:
        value = (
            self.link_type.cardinality.value
            if isinstance(self.link_type.cardinality, Cardinality)
            else str(self.link_type.cardinality)
        )
        if value == Cardinality.ONE_TO_ONE.value:
            return "ONE", "ONE"
        if value == Cardinality.ONE_TO_MANY.value:
            return "MANY", "ONE"
        if value == Cardinality.MANY_TO_ONE.value:
            return "ONE", "MANY"
        return "MANY", "MANY"
