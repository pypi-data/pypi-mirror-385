"""
query_type.py
--------------
Defines QueryType (a first-class metamodel entity) to model saved, parameterized
queries over objects, aligned with Palantir Foundry-style Query Types.

Design principles:
- Metadata-only definition in SQLModel (control plane)
- Parameters and query templates serialized as JSON
- Execution reuses InstancesService.search_objects to materialize results
"""

from __future__ import annotations

from registro import ResourceTypeBaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import JSON, Column, Field


class QueryType(ResourceTypeBaseModel, table=True):
    """
    Represents a saved, parameterized query against an ObjectType.
    The query stores a template of where/orderBy with optional parameter placeholders.
    """

    __resource_type__ = "query-type"
    __tablename__ = "querytype"
    __table_args__ = (UniqueConstraint("api_name", "version", name="uq_querytype_api_version"),)

    # Target ObjectType this query runs against
    target_object_type_api_name: str = Field(index=True)

    # Parameters schema (api_name -> definition dict)
    parameters: dict[str, dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Where template (list of conditions). Values may be literals or parameter refs,
    # e.g., {"param": "minAge"} to refer to execution-time parameters["minAge"].
    where_template: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    # Order-by template (list of {property, direction})
    order_by_template: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    version: int = Field(default=1, ge=1, description="Schema version", index=True)
    is_latest: bool = Field(default=True, description="Latest version flag", index=True)


# Rebuild to resolve forward refs if any
QueryType.model_rebuild()
