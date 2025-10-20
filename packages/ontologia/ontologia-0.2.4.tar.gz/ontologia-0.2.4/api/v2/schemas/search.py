"""
api/v2/schemas/search.py
-------------------------
DTOs for search and (future) analytics requests.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class WhereCondition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    property: str = Field(..., description="Property name to filter on")
    op: Literal[
        "eq",
        "ne",
        "lt",
        "lte",
        "gt",
        "gte",
        "contains",
        "in",
        "isnull",
        "isnotnull",
        "between",
        "startswith",
        "endswith",
    ] = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Value to compare against (list for 'in')")


class OrderBySpec(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    property: str = Field(...)
    direction: Literal["asc", "desc"] = Field("asc")


class TraversalStep(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    link: str = Field(..., description="LinkType API name used for traversal")
    direction: Literal["forward", "reverse"] = Field("forward")
    where: list[WhereCondition] = Field(default_factory=list)
    limit: int | None = Field(default=None, ge=1, le=1000)


class ObjectSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    where: list[WhereCondition] = Field(default_factory=list)
    orderBy: list[OrderBySpec] = Field(default_factory=list)
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    traverse: list[TraversalStep] = Field(default_factory=list)
    asOf: datetime | None = Field(
        default=None,
        description="Timestamp used for bitemporal filtering (valid-from/to).",
        alias="asOf",
    )


# Minimal analytics (placeholder for future work)
class AggregateSpec(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    func: Literal["count", "sum", "avg"]
    property: str | None = None


class AggregateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    objectTypeApiName: str = Field(..., description="API name of the ObjectType to aggregate")
    where: list[WhereCondition] = Field(default_factory=list)
    groupBy: list[str] = Field(default_factory=list)
    metrics: list[AggregateSpec] = Field(default_factory=list)


class AggregateForTypeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    where: list[WhereCondition] = Field(default_factory=list)
    groupBy: list[str] = Field(default_factory=list)
    metrics: list[AggregateSpec] = Field(default_factory=list)


class AggregateRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    group: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, float | int] = Field(default_factory=dict)


class AggregateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rows: list[AggregateRow] = Field(default_factory=list)
