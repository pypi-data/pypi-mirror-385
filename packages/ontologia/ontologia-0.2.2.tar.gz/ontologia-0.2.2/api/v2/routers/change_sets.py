"""API router for change set workflow."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.services.change_set_service import ChangeSetService
from api.v2.schemas.change_sets import (
    ChangeSetApproveRequest,
    ChangeSetCreateRequest,
    ChangeSetListResponse,
    ChangeSetReadResponse,
)

router = APIRouter(tags=["Change Sets"])


def _service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> ChangeSetService:
    return ChangeSetService(session, service="ontology", instance="default", principal=principal)


def _viewer_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> ChangeSetService:
    return ChangeSetService(session, service="ontology", instance="default", principal=principal)


def _admin_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
) -> ChangeSetService:
    return ChangeSetService(session, service="ontology", instance="default", principal=principal)


def _to_response(service: ChangeSetService, record) -> ChangeSetReadResponse:
    dataset = service._dataset_by_rid(record.dataset_rid)
    dataset_api_name = dataset.api_name if dataset else record.api_name
    return ChangeSetReadResponse(
        apiName=record.api_name,
        rid=record.rid,
        name=record.name,
        status=record.status,
        targetObjectType=record.target_object_type,
        baseBranch=record.base_branch,
        description=record.description,
        datasetApiName=dataset_api_name,
        createdAt=record.created_at,
        createdBy=record.created_by,
        approvedAt=record.approved_at,
        payload=dict(record.payload or {}),
    )


@router.post(
    "/change-sets",
    response_model=ChangeSetReadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create change set",
    description="Creates a new change set and associated dataset branch for write-back workflows.",
)
def create_change_set(
    body: ChangeSetCreateRequest,
    service: ChangeSetService = Depends(_service),
) -> ChangeSetReadResponse:
    record = service.create_change_set(body)
    return _to_response(service, record)


@router.get(
    "/change-sets",
    response_model=ChangeSetListResponse,
    summary="List change sets",
    description="Lists change sets with optional status filtering.",
)
def list_change_sets(
    status_filter: str | None = Query(default=None, alias="status"),
    service: ChangeSetService = Depends(_viewer_service),
) -> ChangeSetListResponse:
    items = service.list_change_sets(status_filter)
    data = [_to_response(service, it) for it in items]
    return ChangeSetListResponse(data=data)


@router.post(
    "/change-sets/{changeSetRid}/approve",
    response_model=ChangeSetReadResponse,
    summary="Approve change set",
    description="Marks a change set as approved and advances the associated dataset branch head.",
)
def approve_change_set(
    changeSetRid: str,
    body: ChangeSetApproveRequest,
    service: ChangeSetService = Depends(_admin_service),
) -> ChangeSetReadResponse:
    record = service.approve_change_set(changeSetRid, body)
    dataset = service._dataset_by_rid(record.dataset_rid)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Dataset missing"
        )
    return _to_response(service, record)
