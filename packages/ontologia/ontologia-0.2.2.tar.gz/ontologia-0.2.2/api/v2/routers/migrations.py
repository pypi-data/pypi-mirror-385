"""Endpoints for executing schema migration tasks."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.services.migration_execution_service import MigrationExecutionService
from api.v2.schemas.migrations import (
    MigrationTaskBatchRunRequest,
    MigrationTaskBatchRunResponse,
    MigrationTaskRunRequest,
    MigrationTaskRunResponse,
)

router = APIRouter(tags=["Schema Migrations"])


@router.post(
    "/migrations/tasks/{taskRid}/run",
    response_model=MigrationTaskRunResponse,
    summary="Execute a schema migration task",
    description="Runs a generated MigrationTask with optional dry-run validation.",
)
def run_migration_task_endpoint(
    body: MigrationTaskRunRequest,
    ontologyApiName: str = Path(..., description="Ontology instance name"),
    taskRid: str = Path(..., description="RID of the MigrationTask to execute"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> MigrationTaskRunResponse:
    """Execute a specific MigrationTask."""

    _ = principal  # Reserved for future tenant scoping
    executor = MigrationExecutionService(session)
    result = executor.run_task(
        service="ontology",
        instance=ontologyApiName,
        task_rid=taskRid,
        dry_run=body.dryRun,
        batch_size=body.batchSize,
    )
    return MigrationTaskRunResponse.model_validate(result)


@router.post(
    "/migrations/tasks/run-pending",
    response_model=MigrationTaskBatchRunResponse,
    summary="Execute all pending migration tasks",
    description="Runs every pending MigrationTask for the ontology, optionally in dry-run mode.",
)
def run_pending_migrations_endpoint(
    body: MigrationTaskBatchRunRequest,
    ontologyApiName: str = Path(..., description="Ontology instance name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> MigrationTaskBatchRunResponse:
    """Execute pending MigrationTasks for the ontology."""

    _ = principal
    executor = MigrationExecutionService(session)
    results = executor.run_pending_tasks(
        service="ontology",
        instance=ontologyApiName,
        dry_run=body.dryRun,
        limit=body.limit,
        batch_size=body.batchSize,
    )
    return MigrationTaskBatchRunResponse(
        results=[MigrationTaskRunResponse.model_validate(r) for r in results]
    )
