"""
api/v2/routers/actions.py
--------------------------
Actions endpoints: discovery and execution.

- GET    /objects/{objectTypeApiName}/{pk}/actions
- POST   /objects/{objectTypeApiName}/{pk}/actions/{actionApiName}/execute
"""

from __future__ import annotations

import os

from fastapi import APIRouter, Depends, Header, Path
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.core.settings import get_settings
from api.core.temporal import get_temporal_client
from api.services.actions_service import ActionsService
from api.v2.schemas.actions import (
    ActionExecuteRequest,
    ActionExecuteResponse,
    ActionListResponse,
    ActionParameterDefinition,
    ActionReadResponse,
)

router = APIRouter(tags=["Actions"])


@router.get(
    "/objects/{objectTypeApiName}/{pk}/actions",
    response_model=ActionListResponse,
    summary="List available Actions for an object",
)
def list_actions(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="ObjectType API name"),
    pk: str = Path(..., description="Primary key value"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> ActionListResponse:
    svc = ActionsService(session, service="ontology", instance=ontologyApiName, principal=principal)
    items = svc.list_available_actions(
        objectTypeApiName,
        pk,
        context={
            "user": {
                "id": principal.user_id,
                "roles": principal.roles,
                "tenants": principal.tenants,
            }
        },
    )
    data: list[ActionReadResponse] = []
    for a in items:
        data.append(
            ActionReadResponse(
                apiName=a.api_name,
                rid=a.rid,
                displayName=a.display_name or a.api_name,
                description=getattr(a, "description", None),
                targetObjectType=a.target_object_type_api_name,
                parameters={
                    k: ActionParameterDefinition.model_validate(
                        {
                            "dataType": v.get("dataType"),
                            "displayName": v.get("displayName") or k,
                            "description": v.get("description"),
                            "required": bool(v.get("required", True)),
                        }
                    )
                    for k, v in (a.parameters or {}).items()
                },
            )
        )
    return ActionListResponse(data=data)


@router.post(
    "/objects/{objectTypeApiName}/{pk}/actions/{actionApiName}/execute",
    response_model=ActionExecuteResponse,
    summary="Execute an Action for an object",
)
async def execute_action(
    body: ActionExecuteRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="ObjectType API name"),
    pk: str = Path(..., description="Primary key value"),
    actionApiName: str = Path(..., description="Action API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
    temporal_client=Depends(get_temporal_client),
) -> ActionExecuteResponse:
    svc = ActionsService(
        session,
        service="ontology",
        instance=ontologyApiName,
        temporal_client=temporal_client,
        principal=principal,
    )
    params = dict(body.parameters or {})
    settings = get_settings()
    # Allow env var to override cached settings for testability and runtime toggles
    use_temporal = settings.use_temporal_actions or os.getenv("USE_TEMPORAL_ACTIONS", "0") in (
        "1",
        "true",
        "True",
    )
    user_ctx = {
        "id": principal.user_id,
        "roles": principal.roles,
        "tenants": principal.tenants,
    }
    if use_temporal:
        result = await svc.execute_action_async(
            objectTypeApiName, pk, actionApiName, params, user=user_ctx
        )
    else:
        result = svc.execute_action(objectTypeApiName, pk, actionApiName, params, user=user_ctx)
    # The executor may return arbitrary keys; Pydantic model allows extra
    return ActionExecuteResponse.model_validate(result)


@router.post(
    "/objects/{objectTypeApiName}/{pk}/actions/{actionApiName}/start",
    response_model=ActionExecuteResponse,
    summary="Start an Action asynchronously (Temporal)",
)
async def start_action(
    body: ActionExecuteRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="ObjectType API name"),
    pk: str = Path(..., description="Primary key value"),
    actionApiName: str = Path(..., description="Action API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
    temporal_client=Depends(get_temporal_client),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> ActionExecuteResponse:
    settings = get_settings()
    use_temporal = settings.use_temporal_actions or os.getenv("USE_TEMPORAL_ACTIONS", "0") in (
        "1",
        "true",
        "True",
    )
    if not use_temporal:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Temporal is disabled (USE_TEMPORAL_ACTIONS)")

    svc = ActionsService(
        session,
        service="ontology",
        instance=ontologyApiName,
        temporal_client=temporal_client,
        principal=principal,
    )
    params = dict(body.parameters or {})
    ids = await svc.start_action_async(
        objectTypeApiName,
        pk,
        actionApiName,
        params,
        user={
            "id": principal.user_id,
            "roles": principal.roles,
            "tenants": principal.tenants,
        },
        idempotency_key=idempotency_key,
    )
    # Reuse ActionExecuteResponse with permissive extra fields
    return ActionExecuteResponse.model_validate({"status": "started", **ids})


@router.get(
    "/actions/runs/{workflowId}",
    response_model=ActionExecuteResponse,
    summary="Get Action run status (Temporal)",
)
async def get_action_run_status(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    workflowId: str = Path(..., description="Temporal workflow ID"),
    runId: str | None = None,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
    temporal_client=Depends(get_temporal_client),
) -> ActionExecuteResponse:
    settings = get_settings()
    use_temporal = settings.use_temporal_actions or os.getenv("USE_TEMPORAL_ACTIONS", "0") in (
        "1",
        "true",
        "True",
    )
    if not use_temporal:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Temporal is disabled (USE_TEMPORAL_ACTIONS)")

    svc = ActionsService(session, service="ontology", instance=ontologyApiName, principal=principal)
    out = await svc.get_action_status(workflow_id=workflowId, run_id=runId)
    return ActionExecuteResponse.model_validate(out)


@router.post(
    "/actions/runs/{workflowId}:cancel",
    response_model=ActionExecuteResponse,
    summary="Cancel Action run (Temporal)",
)
async def cancel_action_run(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    workflowId: str = Path(..., description="Temporal workflow ID"),
    runId: str | None = None,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
    temporal_client=Depends(get_temporal_client),
) -> ActionExecuteResponse:
    settings = get_settings()
    use_temporal = settings.use_temporal_actions or os.getenv("USE_TEMPORAL_ACTIONS", "0") in (
        "1",
        "true",
        "True",
    )
    if not use_temporal:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Temporal is disabled (USE_TEMPORAL_ACTIONS)")

    svc = ActionsService(session, service="ontology", instance=ontologyApiName, principal=principal)
    out = await svc.cancel_action_run(workflow_id=workflowId, run_id=runId)
    return ActionExecuteResponse.model_validate(out)
