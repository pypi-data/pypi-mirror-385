"""
link_property_type.py
---------------------
Property definitions for LinkType (edge) properties.
"""

from typing import Any, Optional

from pydantic import ConfigDict
from registro import ResourceTypeBaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import JSON, Column, Field, Relationship


class LinkPropertyType(ResourceTypeBaseModel, table=True):
    __resource_type__ = "link-property-type"
    __tablename__ = "linkpropertytype"

    __table_args__ = (
        UniqueConstraint("link_type_rid", "api_name", name="uq_linkpropertytype_link_api"),
    )

    # Pydantic v2 config
    model_config = ConfigDict(extra="forbid", json_schema_extra={"exclude": {"link_type": True}})

    # Data type and validation (keep parity with PropertyType)
    data_type: str = Field(...)
    data_type_config: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column("data_type_config", JSON)
    )
    description: str | None = None
    quality_checks: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    required: bool = False

    # Parent LinkType
    link_type_rid: str = Field(foreign_key="linktype.rid", index=True)
    link_type_api_name: str = Field(index=True)
    link_type: Optional["LinkType"] = Relationship(
        back_populates="link_property_types",
        sa_relationship_kwargs={"cascade": "all, delete", "lazy": "selectin"},
    )


# Late import to avoid cycles
from ontologia.domain.metamodels.types.link_type import LinkType  # noqa: E402

LinkPropertyType.model_rebuild()
