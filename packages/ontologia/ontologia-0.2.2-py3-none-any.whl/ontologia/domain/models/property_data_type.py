"""
property_data_type.py
-------------------
This module defines the data type system for properties in the ontology.
It provides a set of base data types and composite types (struct, array)
that can be used to define property schemas.

Key Features:
- Basic types (string, integer, double, boolean, date, timestamp)
- Composite types (struct, array)
- Type discrimination using Pydantic's discriminated unions
- JSON serialization support
"""

from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# --- Base Data Type Model ---
class DataTypeBase(BaseModel):
    """Base class for all data types with common configuration."""

    model_config = ConfigDict(
        frozen=True,  # Make instances immutable
        extra="forbid",  # No extra fields allowed
        validate_assignment=True,  # Validate on attribute assignment
        json_schema_extra={"examples": []},  # For API documentation
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert data type to a dictionary representation."""
        return self.model_dump(exclude_none=True)


# --- Basic Data Types ---
class StringType(DataTypeBase):
    """String data type for text values."""

    type: Literal["string"] = "string"

    def __repr__(self):
        return "StringType()"


class IntegerType(DataTypeBase):
    """Integer data type for whole numbers."""

    type: Literal["integer"] = "integer"

    def __repr__(self):
        return "IntegerType()"


class DoubleType(DataTypeBase):
    """Double data type for floating point numbers."""

    type: Literal["double"] = "double"

    def __repr__(self):
        return "DoubleType()"


class BooleanType(DataTypeBase):
    """Boolean data type for true/false values."""

    type: Literal["boolean"] = "boolean"

    def __repr__(self):
        return "BooleanType()"


class DateType(DataTypeBase):
    """Date data type for calendar dates."""

    type: Literal["date"] = "date"

    def __repr__(self):
        return "DateType()"


class TimestampType(DataTypeBase):
    """Timestamp data type for date-time values."""

    type: Literal["timestamp"] = "timestamp"

    def __repr__(self):
        return "TimestampType()"


# --- Composite Data Types ---
class StructFieldType(DataTypeBase):
    """Field definition for struct types."""

    api_name: str = Field(..., min_length=1, max_length=255)
    data_type: "PropertyDataType"


class StructType(DataTypeBase):
    """Struct data type for composite objects."""

    type: Literal["struct"] = "struct"
    struct_field_types: list[StructFieldType] = Field(..., min_length=1)


class ArrayType(DataTypeBase):
    """Array data type for lists of values."""

    type: Literal["array"] = "array"
    sub_type: "PropertyDataType"


# --- Type Union ---
PropertyDataType = Annotated[
    StringType
    | IntegerType
    | DoubleType
    | BooleanType
    | DateType
    | TimestampType
    | StructType
    | ArrayType,
    Field(discriminator="type"),
]

# Type registry for serialization/deserialization
TYPE_REGISTRY: dict[str, type[DataTypeBase]] = {
    "string": StringType,
    "integer": IntegerType,
    "double": DoubleType,
    "boolean": BooleanType,
    "date": DateType,
    "timestamp": TimestampType,
    "struct": StructType,
    "array": ArrayType,
}


def create_data_type(type_name: str, **kwargs) -> PropertyDataType:
    """Create a data type instance from its type name and optional parameters."""
    if type_name not in TYPE_REGISTRY:
        raise ValueError(f"Unknown type: {type_name}")
    return TYPE_REGISTRY[type_name](**kwargs)


def get_type_name(data_type: PropertyDataType) -> str:
    """Get the string name of a data type."""
    return data_type.type


def create_date_type(value: str | date | None = None) -> DateType:
    """Create a date type, handling coercion from date objects."""
    if value is None:
        return DateType()
    elif isinstance(value, date) and not isinstance(value, datetime):
        # Convert date to ISO string format
        return DateType(type="date")
    else:
        return DateType(type="date")


def create_timestamp_type(value: str | datetime | None = None) -> TimestampType:
    """Create a timestamp type, handling coercion from datetime objects."""
    if value is None:
        return TimestampType()
    elif isinstance(value, datetime):
        # Convert datetime to ISO string format
        return TimestampType(type="timestamp")
    else:
        return TimestampType(type="timestamp")


# Update forward references
StructFieldType.model_rebuild()
ArrayType.model_rebuild()
