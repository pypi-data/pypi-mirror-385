"""
interface_type.py
------------------
Defines InterfaceType (a first-class metamodel entity) and the association
link model between ObjectType and InterfaceType.

Interfaces are semantic contracts that ObjectTypes can implement. They are
stored in SQLModel and exposed via the API. Properties are modeled as a JSON
contract to keep the type decoupled from concrete PropertyType persistence.
"""

from pydantic import BaseModel, ConfigDict
from registro import ResourceTypeBaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import JSON, Column, Field, Relationship

from ontologia.domain.metamodels.types.object_type_interface_link import ObjectTypeInterfaceLink


class InterfacePropertyDefinition(BaseModel):
    """
    Lightweight property contract for interfaces.
    This mirrors the API's PropertyDefinition shape minimally.
    """

    model_config = ConfigDict(populate_by_name=True)

    dataType: str
    displayName: str
    description: str | None = None


class InterfaceType(ResourceTypeBaseModel, table=True):
    """
    Represents an interface (semantic contract) that can be implemented by ObjectTypes.
    """

    __resource_type__ = "interface-type"
    __tablename__ = "interfacetype"
    __table_args__ = (UniqueConstraint("api_name", "version", name="uq_interfacetype_api_version"),)

    # Pydantic v2 config
    model_config = ConfigDict(extra="forbid")

    # Optional description for display/UX
    description: str | None = None

    # Optional: JSON property contract (api_name -> InterfacePropertyDefinition)
    properties: dict[str, InterfacePropertyDefinition] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )

    version: int = Field(default=1, ge=1, description="Schema version", index=True)
    is_latest: bool = Field(default=True, description="Latest version flag", index=True)

    # Back-reference to implementing object types
    object_types: list["ObjectType"] = Relationship(
        back_populates="interfaces",
        link_model=ObjectTypeInterfaceLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


# Late imports to avoid circular dependencies
from ontologia.domain.metamodels.types.object_type import ObjectType  # noqa: E402

# Rebuild model to resolve forward references
InterfaceType.model_rebuild()
