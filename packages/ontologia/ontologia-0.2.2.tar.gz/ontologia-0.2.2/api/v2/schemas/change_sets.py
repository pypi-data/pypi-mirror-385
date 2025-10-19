"""Pydantic schemas for change set workflow."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChangeSetCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., description="Human-friendly change set name")
    targetObjectType: str = Field(..., description="ObjectType impacted by the change set")
    description: str | None = Field(default=None, description="Optional description")
    baseBranch: str | None = Field(
        default="draft",
        description="Dataset branch used as the base for this change set",
    )
    changes: list[dict[str, Any]] = Field(default_factory=list)


class ChangeSetApproveRequest(BaseModel):
    approvedBy: str | None = Field(default=None, description="User approving the change set")
    commitMessage: str | None = Field(default=None, description="Optional approval note")


class ChangeSetReadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    apiName: str
    rid: str
    name: str
    status: str
    targetObjectType: str = Field(alias="targetObjectType")
    baseBranch: str | None = None
    description: str | None = None
    datasetApiName: str
    createdAt: datetime
    createdBy: str | None = None
    approvedAt: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ChangeSetListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data: list[ChangeSetReadResponse] = Field(default_factory=list)
