"""
api/v2/routers/objects.py
-------------------------
Endpoints REST para Instâncias de Objetos (compatível com Foundry-like API).

Endpoints:
- PUT    /objects/{objectTypeApiName}/{pk}  - Upsert de instância (PUT semantics)
- GET    /objects/{objectTypeApiName}/{pk}  - Busca instância por OT+PK
- DELETE /objects/{objectTypeApiName}/{pk}  - Deleta instância por OT+PK
- GET    /objects                           - Lista todas as instâncias (opcional filtro por objectType)
- GET    /objects/{objectTypeApiName}       - Lista instâncias de um ObjectType
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, status
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.handlers.instances import (
    ObjectInstanceCommandService,
    ObjectInstanceQueryService,
    get_instance_admin_command_service,
    get_instance_command_service,
    get_instance_query_service,
)
from api.services.analytics_service import AnalyticsService
from api.v2.schemas.bulk import ObjectBulkLoadRequest
from api.v2.schemas.instances import (
    ObjectListResponse,
    ObjectReadResponse,
    ObjectUpsertRequest,
)
from api.v2.schemas.search import (
    AggregateForTypeRequest,
    AggregateRequest,
    AggregateResponse,
    ObjectSearchRequest,
)

router = APIRouter(tags=["Objects"])


@router.put(
    "/objects/{objectTypeApiName}/{pk}",
    response_model=ObjectReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upsert object instance",
    description="Creates or replaces an object instance by ObjectType and primary key.",
)
def upsert_object_instance(
    body: ObjectUpsertRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    pk: str = Path(..., description="Primary key value of the instance"),
    command_service: ObjectInstanceCommandService = Depends(get_instance_command_service),
) -> ObjectReadResponse:
    return command_service.upsert_object(objectTypeApiName, pk, body)


@router.get(
    "/objects/{objectTypeApiName}/{pk}",
    response_model=ObjectReadResponse,
    summary="Get object instance",
    description="Returns a single object instance by ObjectType and primary key.",
)
def get_object_instance(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    pk: str = Path(..., description="Primary key value of the instance"),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    changeSetRid: str | None = Header(
        default=None,
        alias="X-Ontologia-ChangeSet-Rid",
        description="RID of ChangeSet overlay for what-if scenarios",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
) -> ObjectReadResponse:
    obj = query_service.get_object(
        objectTypeApiName,
        pk,
        as_of=validAt,
        change_set_rid=changeSetRid,
    )
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return obj


@router.delete(
    "/objects/{objectTypeApiName}/{pk}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete object instance",
    description="Deletes an object instance by ObjectType and primary key.",
)
def delete_object_instance(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    pk: str = Path(..., description="Primary key value of the instance"),
    command_service: ObjectInstanceCommandService = Depends(get_instance_admin_command_service),
):
    ok = command_service.delete_object(objectTypeApiName, pk)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return None


@router.get(
    "/objects",
    response_model=ObjectListResponse,
    summary="List object instances",
    description="Lists object instances; optionally filter by objectType via query param.",
)
def list_objects(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectType: str | None = Query(default=None, description="Filter by ObjectType apiName"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    changeSetRid: str | None = Header(
        default=None,
        alias="X-Ontologia-ChangeSet-Rid",
        description="RID of ChangeSet overlay for what-if scenarios",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
) -> ObjectListResponse:
    return query_service.list_objects(
        object_type_api_name=objectType,
        limit=limit,
        offset=offset,
        valid_at=validAt,
        change_set_rid=changeSetRid,
    )


@router.get(
    "/objects/{objectTypeApiName}",
    response_model=ObjectListResponse,
    summary="List object instances by type",
    description="Lists object instances for a specific ObjectType.",
)
def list_objects_by_type(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    changeSetRid: str | None = Header(
        default=None,
        alias="X-Ontologia-ChangeSet-Rid",
        description="RID of ChangeSet overlay for what-if scenarios",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
) -> ObjectListResponse:
    return query_service.list_objects(
        object_type_api_name=objectTypeApiName,
        limit=limit,
        offset=offset,
        valid_at=validAt,
        change_set_rid=changeSetRid,
    )


@router.post(
    "/objects/{objectTypeApiName}/search",
    response_model=ObjectListResponse,
    summary="Search object instances",
    description="Search for object instances by properties with filtering, ordering, and pagination.",
)
def search_objects(
    body: ObjectSearchRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    changeSetRid: str | None = Header(
        default=None,
        alias="X-Ontologia-ChangeSet-Rid",
        description="RID of ChangeSet overlay for what-if scenarios",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
) -> ObjectListResponse:
    return query_service.search_objects(
        objectTypeApiName,
        body,
        change_set_rid=changeSetRid,
    )


@router.post(
    "/objects/{objectTypeApiName}/aggregate",
    response_model=AggregateResponse,
    summary="Aggregate over object instances of a type",
    description="Execute COUNT/SUM/AVG with optional groupBy and filters for a specific ObjectType.",
)
def aggregate_for_type(
    body: AggregateForTypeRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> AggregateResponse:
    svc = AnalyticsService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    req = AggregateRequest(
        objectTypeApiName=objectTypeApiName,
        where=body.where,
        groupBy=body.groupBy,
        metrics=body.metrics,
    )
    return svc.aggregate(req)


@router.post(
    "/objects/{objectTypeApiName}/load",
    response_model=ObjectListResponse,
    summary="Bulk load (upsert) objects",
    description="Create or update multiple objects in a single call.",
)
def bulk_load_objects(
    body: ObjectBulkLoadRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    command_service: ObjectInstanceCommandService = Depends(get_instance_command_service),
) -> ObjectListResponse:
    return command_service.bulk_load_objects(objectTypeApiName, body)


@router.get(
    "/objects/{objectTypeApiName}/{pk}/{linkTypeApiName}",
    response_model=ObjectListResponse,
    summary="Get linked objects",
    description="Traverse from a starting object along a LinkType to retrieve connected objects.",
)
def get_linked_objects(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the starting ObjectType"),
    pk: str = Path(..., description="Primary key of the starting object instance"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType used for traversal"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
) -> ObjectListResponse:
    return query_service.get_linked_objects(
        objectTypeApiName,
        pk,
        linkTypeApiName,
        limit=limit,
        offset=offset,
        valid_at=validAt,
    )
