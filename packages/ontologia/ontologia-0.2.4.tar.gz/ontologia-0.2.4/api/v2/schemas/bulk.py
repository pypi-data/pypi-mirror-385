"""
api/v2/schemas/bulk.py
----------------------
DTOs for bulk load operations on objects and links.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ObjectLoadItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pk: str = Field(..., description="Primary key value")
    properties: dict[str, Any] = Field(default_factory=dict)


class ObjectBulkLoadRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ObjectLoadItem] = Field(default_factory=list)


class LinkLoadItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    fromPk: str
    toPk: str
    properties: dict[str, Any] | None = Field(default_factory=dict)


class LinkBulkLoadRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[LinkLoadItem] = Field(default_factory=list)
    mode: Literal["create", "delete"] = Field("create")
