"""
instances/dtos.py
-----------------
Pydantic DTOs for instance-layer models. These represent in-memory data transfer
objects and are decoupled from the persistence layer (SQLModel tables).

They provide classmethods to convert from the SQLModel entities when needed.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

# Import type hints lazily in functions to avoid circular imports.

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from ontologia.domain.metamodels.instances.models_sql import LinkedObject, ObjectInstance
    from ontologia.domain.metamodels.instances.object_type_data_source import (
        ObjectTypeDataSource,
    )


class ObjectTypeDataSourceDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Resource identity (optional but useful for tracing)
    rid: str | None = None
    service: str | None = None
    instance: str | None = None
    api_name: str | None = None
    display_name: str | None = None

    # Core fields
    object_type_rid: str
    dataset_rid: str

    # Sync metadata
    last_sync_time: datetime | None = None
    sync_status: str | None = "pending"

    # Column/property mapping (dataset column -> object property)
    property_mappings: dict[str, str] | None = None

    @classmethod
    def from_model(cls, m: ObjectTypeDataSource) -> ObjectTypeDataSourceDTO:
        # Local import to avoid import cycles
        from ontologia.domain.metamodels.instances.object_type_data_source import (
            ObjectTypeDataSource,
        )

        if not isinstance(m, ObjectTypeDataSource):  # pragma: no cover - guard
            raise TypeError("expected ObjectTypeDataSource model instance")
        return cls(
            rid=getattr(m, "rid", None),
            service=getattr(m, "service", None),
            instance=getattr(m, "instance", None),
            api_name=getattr(m, "api_name", None),
            display_name=getattr(m, "display_name", None),
            object_type_rid=m.object_type_rid,
            dataset_rid=m.dataset_rid,
            last_sync_time=m.last_sync_time,
            sync_status=m.sync_status,
            property_mappings=(m.property_mappings or None),
        )


class ObjectInstanceDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rid: str | None = None
    service: str | None = None
    instance: str | None = None
    api_name: str | None = None
    display_name: str | None = None

    object_type_api_name: str
    object_type_rid: str
    pk_value: str
    data: dict[str, Any]

    @classmethod
    def from_model(cls, m: ObjectInstance) -> ObjectInstanceDTO:
        from ontologia.domain.metamodels.instances.models_sql import ObjectInstance

        if not isinstance(m, ObjectInstance):  # pragma: no cover - guard
            raise TypeError("expected ObjectInstance model instance")
        return cls(
            rid=getattr(m, "rid", None),
            service=getattr(m, "service", None),
            instance=getattr(m, "instance", None),
            api_name=getattr(m, "api_name", None),
            display_name=getattr(m, "display_name", None),
            object_type_api_name=m.object_type_api_name,
            object_type_rid=m.object_type_rid,
            pk_value=m.pk_value,
            data=dict(getattr(m, "data", {}) or {}),
        )


class LinkedObjectDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rid: str | None = None
    service: str | None = None
    instance: str | None = None
    api_name: str | None = None
    display_name: str | None = None

    link_type_api_name: str
    link_type_rid: str
    from_object_rid: str
    to_object_rid: str

    @classmethod
    def from_model(cls, m: LinkedObject) -> LinkedObjectDTO:
        from ontologia.domain.metamodels.instances.models_sql import LinkedObject

        if not isinstance(m, LinkedObject):  # pragma: no cover - guard
            raise TypeError("expected LinkedObject model instance")
        return cls(
            rid=getattr(m, "rid", None),
            service=getattr(m, "service", None),
            instance=getattr(m, "instance", None),
            api_name=getattr(m, "api_name", None),
            display_name=getattr(m, "display_name", None),
            link_type_api_name=m.link_type_api_name,
            link_type_rid=m.link_type_rid,
            from_object_rid=m.from_object_rid,
            to_object_rid=m.to_object_rid,
        )


__all__ = [
    "ObjectTypeDataSourceDTO",
    "ObjectInstanceDTO",
    "LinkedObjectDTO",
]
