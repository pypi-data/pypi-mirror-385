"""Pydantic schemas for schema migration execution endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MigrationTaskRunRequest(BaseModel):
    dryRun: bool = Field(default=False, description="Validate without applying changes")
    batchSize: int | None = Field(
        default=None,
        ge=1,
        le=10_000,
        description="Maximum number of instances processed per batch",
    )


class MigrationTaskRunResponse(BaseModel):
    taskRid: str
    objectTypeApiName: str
    dryRun: bool
    totalInstances: int
    updatedCount: int
    failedCount: int
    errors: list[str] = Field(default_factory=list)
    operationsPlanned: int
    taskStatus: str


class MigrationTaskBatchRunRequest(BaseModel):
    dryRun: bool = Field(default=False, description="Validate without applying changes")
    limit: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="Maximum number of tasks to process",
    )
    batchSize: int | None = Field(
        default=None,
        ge=1,
        le=10_000,
        description="Maximum number of instances processed per batch",
    )


class MigrationTaskBatchRunResponse(BaseModel):
    results: list[MigrationTaskRunResponse] = Field(default_factory=list)
