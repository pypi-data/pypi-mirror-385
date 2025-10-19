"""
property_type.py
---------------
This module defines the PropertyType model which represents metadata about
properties in the ontology. It integrates with the data type system and
provides validation and persistence capabilities.

Key Features:
- Property metadata (name, description, etc.)
- Integration with data type system
- Validation rules (required, primary key)
- Relationship with ObjectType
- JSON serialization support
"""

from typing import Any, Optional

from pydantic import ConfigDict, ValidationInfo, field_validator
from registro import ResourceTypeBaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import JSON, Column, Field, Relationship, Session, select

from ontologia.domain.models.property_data_type import (
    TYPE_REGISTRY,
    PropertyDataType,
    create_data_type,
    get_type_name,
)


class PropertyType(ResourceTypeBaseModel, table=True):
    """
    Represents a property definition in the ontology.
    Properties belong to ObjectTypes and define their data structure.
    """

    __resource_type__ = "property-type"
    __table_args__ = (
        UniqueConstraint("object_type_rid", "api_name", name="uq_propertytype_object_api"),
    )

    # Pydantic v2 config
    model_config = ConfigDict(
        extra="forbid", json_schema_extra={"exclude": {"object_type_rid", "object_type"}}
    )

    # Data type and validation
    data_type: str = Field(...)  # Store as string
    data_type_config: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column("data_type_config", JSON)
    )
    description: str | None = None
    # Data quality rules expressed as simple strings, e.g.:
    # - "not_null"
    # - "in[OPEN,CLOSED]"
    # - "between[0,100]"
    # - "min_length[3]", "max_length[50]"
    quality_checks: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    is_primary_key: bool = False
    required: bool = False

    # Optional dynamic derivation expression evaluated on reads
    derivation_script: str | None = None

    # Foreign Key Reference (optional)
    references_object_type_api_name: str | None = Field(
        default=None,
        description="If this property is a foreign key, specifies the ObjectType it references",
    )

    # Relationship with ObjectType
    object_type_rid: str = Field(foreign_key="objecttype.rid", index=True)
    object_type_api_name: str = Field(index=True)  # Added field for direct API name reference
    object_type: Optional["ObjectType"] = Relationship(
        back_populates="property_types",
        sa_relationship_kwargs={"cascade": "all, delete", "lazy": "selectin"},
    )

    # Class variable to store session for validation

    def model_post_init(self, __context: Any) -> None:
        """
        Validate fields after initialization.
        SQLModel with table=True skips Pydantic validators during __init__ for performance,
        so we validate here in model_post_init which is called after initialization.
        """
        super().model_post_init(__context)

        # Validate object_type_api_name
        if not self.object_type_api_name or not self.object_type_api_name.isidentifier():
            raise ValueError("object_type_api_name must be a valid Python identifier")

        # Validate references_object_type_api_name if provided
        if (
            self.references_object_type_api_name is not None
            and not self.references_object_type_api_name.isidentifier()
        ):
            raise ValueError("references_object_type_api_name must be a valid Python identifier")

    def _get_object_type_by_rid(self, session: Session) -> "ObjectType":
        """Internal method to get the object type by RID."""
        stmt = select(ObjectType).where(ObjectType.rid == self.object_type_rid)
        obj_type = session.exec(stmt).first()
        if not obj_type:
            raise ValueError(f"Object type with RID '{self.object_type_rid}' not found")
        return obj_type

    def _get_object_type_by_api_name(self, session: Session) -> "ObjectType":
        from registro.core.resource import Resource

        stmt = (
            select(ObjectType)
            .join(Resource, Resource.rid == ObjectType.rid)
            .where(
                Resource.service == self.service,
                Resource.instance == self.instance,
                ObjectType.api_name == self.object_type_api_name,
            )
        )
        obj_type = session.exec(stmt).first()
        if not obj_type:
            raise ValueError(f"Object type with api_name '{self.object_type_api_name}' not found")
        return obj_type

    def link_object_type(self, session: Session) -> None:
        """
        Link this property to its object type.
        This should be called after the instance is created and before committing to the database.
        """
        # If object_type is already set, use it
        if self.object_type:
            # Ensure object_type_rid matches
            self.object_type_rid = self.object_type.rid
            # Ensure object_type_api_name matches
            self.object_type_api_name = self.object_type.api_name
            return

        # Try to get object type by RID first
        try:
            obj_type = self._get_object_type_by_rid(session)
            self.object_type = obj_type
            self.object_type_api_name = obj_type.api_name
            return
        except ValueError:
            # If that fails, try by api_name
            if self.object_type_api_name:
                obj_type = self._get_object_type_by_api_name(session)
                self.object_type = obj_type
                self.object_type_rid = obj_type.rid
                return

        # If we get here, we couldn't find the object type
        raise ValueError(
            f"Could not find object type for property '{self.api_name}'. Please provide either object_type_rid or object_type_api_name."
        )

    @field_validator("data_type")
    def validate_data_type(cls, v):
        """Validate data type name and ensure it exists in registry."""
        if v not in TYPE_REGISTRY:
            raise ValueError(
                f"Invalid data type: {v}. Must be one of: {', '.join(TYPE_REGISTRY.keys())}"
            )
        return v

    @field_validator("data_type_config")
    def validate_data_type_config(cls, v, info: ValidationInfo):
        """Validate data type configuration."""
        dt = (info.data or {}).get("data_type")
        if dt:
            try:
                # Try to create the data type with the config to validate it
                create_data_type(dt, **(v or {}))
            except Exception as e:
                raise ValueError(f"Invalid data type configuration: {e}") from e
        return v

    @field_validator("object_type", check_fields=False)
    def validate_object_type(cls, v, info: ValidationInfo):
        """Validate that if object_type is provided, it matches the api_name and rid."""
        if v is not None:
            data = info.data or {}
            # Check api_name if provided
            if data.get("object_type_api_name") and v.api_name != data["object_type_api_name"]:
                raise ValueError(
                    f"Provided object_type.api_name '{v.api_name}' does not match "
                    f"object_type_api_name '{data['object_type_api_name']}'"
                )
            # Check rid if provided
            if data.get("object_type_rid") and v.rid != data["object_type_rid"]:
                raise ValueError(
                    f"Provided object_type.rid '{v.rid}' does not match "
                    f"object_type_rid '{data['object_type_rid']}'"
                )
        return v

    def get_data_type_instance(self) -> PropertyDataType:
        """Get the property data type instance."""
        return create_data_type(self.data_type, **self.data_type_config)

    def set_data_type_instance(self, value: PropertyDataType) -> None:
        """Set the data type from a PropertyDataType instance."""
        self.data_type = get_type_name(value)
        self.data_type_config = value.to_dict()
        # Remove type from config as it's stored separately
        self.data_type_config.pop("type", None)

    def to_dict(self) -> dict[str, Any]:
        """Convert property type to a dictionary representation."""
        return {
            "api_name": self.api_name,
            "display_name": self.display_name,
            "description": self.description,
            "data_type": self.data_type,
            "data_type_config": self.data_type_config,
            "is_primary_key": self.is_primary_key,
            "required": self.required,
            "object_type_api_name": self.object_type_api_name,
            "object_type_rid": self.object_type_rid,
        }

    @classmethod
    def validate_unique_object_type_api_name(
        cls, object_type_rid: str, api_name: str, session
    ) -> None:
        """Validate that PropertyType.api_name is unique per object_type_rid."""
        from sqlmodel import select

        existing = session.exec(
            select(cls).where(cls.object_type_rid == object_type_rid, cls.api_name == api_name)
        ).first()
        if existing:
            raise ValueError(
                f"PropertyType with api_name '{api_name}' already exists for object_type_rid '{object_type_rid}'"
            )

    def validate_unique_before_save(self, session) -> None:
        """Validate uniqueness constraints before saving."""
        self.validate_unique_object_type_api_name(self.object_type_rid, self.api_name, session)


# Import at the end to avoid circular imports
from ontologia.domain.metamodels.types.object_type import ObjectType  # noqa: E402

# Rebuild model to resolve forward references
PropertyType.model_rebuild()
