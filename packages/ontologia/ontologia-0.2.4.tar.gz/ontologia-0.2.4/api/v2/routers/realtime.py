"""Hybrid endpoints combining real-time state with historical context."""

from __future__ import annotations

import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.dependencies.realtime import get_entity_manager, get_runtime
from api.services.hybrid_snapshot_service import HybridSnapshotService
from api.services.instances_service import InstancesService
from api.v2.schemas.realtime import HybridEntityResponse, RealtimeEventResponse
from ontologia_realtime.entity_manager import EntityManager
from ontologia_realtime.runtime import RealTimeRuntime

router = APIRouter(tags=["Realtime"])


def _serialize_event(event) -> RealtimeEventResponse:
    return RealtimeEventResponse(
        sequence=event.sequence,
        eventType=event.event_type,
        entityId=event.entity_id,
        objectType=event.object_type,
        provenance=event.provenance,
        updatedAt=event.updated_at,
        expiresAt=event.expires_at,
        components={key: dict(value) for key, value in event.components.items()},
        metadata=dict(event.metadata),
    )


@router.get(
    "/realtime/entities/{entityId}",
    response_model=HybridEntityResponse,
    summary="Fetch a hybrid entity snapshot",
    description="Merge the in-memory entity state with historical context in a single response.",
)
async def get_hybrid_entity(
    entityId: str = Path(..., description="Entity identifier"),
    ontologyApiName: str = Path(..., description="Ontology API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
    manager: EntityManager = Depends(get_entity_manager),
) -> HybridEntityResponse:
    instances = InstancesService(
        session,
        service="ontology",
        instance=ontologyApiName,
        principal=principal,
    )
    service = HybridSnapshotService(manager, instances)
    view = await service.get_entity(entityId)
    if view is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity '{entityId}' not found in real-time state",
        )
    return HybridEntityResponse(
        entityId=view.entity_id,
        objectType=view.object_type,
        provenance=view.provenance,
        expiresAt=view.expires_at,
        updatedAt=view.updated_at,
        components=view.components,
        historical=view.historical,
    )


@router.get(
    "/realtime/events",
    response_model=list[RealtimeEventResponse],
    summary="List recent real-time events",
    description="Fetch the latest events captured in the real-time journal for operator dashboards.",
)
async def list_realtime_events(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return"),
    objectTypes: list[str] | None = Query(
        default=None,
        description="Optional object type filters",
    ),
    entityIds: list[str] | None = Query(
        default=None,
        description="Optional entity identifier filters",
    ),
    runtime: RealTimeRuntime = Depends(get_runtime),
) -> list[RealtimeEventResponse]:
    object_types = set(objectTypes) if objectTypes else None
    entity_ids = set(entityIds) if entityIds else None
    events = await runtime.get_recent_events(
        limit=limit,
        object_types=object_types,
        entity_ids=entity_ids,
    )
    return [_serialize_event(event) for event in events]


@router.websocket("/realtime/ws")
async def realtime_websocket(
    websocket: WebSocket,
    ontologyApiName: str,
    runtime: RealTimeRuntime = Depends(get_runtime),
) -> None:
    await websocket.accept()
    query = websocket.query_params
    object_types_param = query.get("objectTypes")
    object_types = (
        {part.strip() for part in object_types_param.split(",") if part.strip()}
        if object_types_param
        else None
    )
    entity_ids_param = query.get("entityIds")
    entity_ids = (
        {part.strip() for part in entity_ids_param.split(",") if part.strip()}
        if entity_ids_param
        else None
    )
    queue = runtime.subscribe_events()
    try:
        while True:
            event = await queue.get()
            if object_types and event.object_type not in object_types:
                continue
            if entity_ids and event.entity_id not in entity_ids:
                continue
            await websocket.send_json(_serialize_event(event).model_dump(mode="json"))
    except WebSocketDisconnect:
        pass
    except Exception:  # pragma: no cover - resilience guard
        logger = logging.getLogger(__name__)
        logger.exception("Realtime websocket connection terminated unexpectedly")
    finally:
        runtime.unsubscribe_events(queue)
