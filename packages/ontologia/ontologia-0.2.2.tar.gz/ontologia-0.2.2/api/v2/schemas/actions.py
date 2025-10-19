"""
api/v2/schemas/actions.py
--------------------------
Pydantic DTOs for Actions (Foundry-like) in API v2.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ActionParameterDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dataType: Literal["string", "integer", "double", "boolean", "date", "timestamp"]
    displayName: str
    description: str | None = None
    required: bool | None = True


class ActionReadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    apiName: str
    rid: str
    displayName: str
    description: str | None = None
    targetObjectType: str
    parameters: dict[str, ActionParameterDefinition] = Field(default_factory=dict)


class ActionListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data: list[ActionReadResponse] = Field(default_factory=list)
    nextPageToken: str | None = None


class ActionExecuteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    parameters: dict[str, Any] | None = Field(default_factory=dict)


class ActionExecuteResponse(BaseModel):
    # Allow arbitrary keys from action executors
    model_config = ConfigDict(extra="allow")
