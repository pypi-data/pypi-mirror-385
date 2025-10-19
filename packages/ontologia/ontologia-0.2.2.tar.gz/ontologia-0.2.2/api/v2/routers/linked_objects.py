"""
api/v2/routers/linked_objects.py
---------------------------------
Endpoints REST para LinkedObjects (relações entre instâncias).

Endpoints:
- POST   /links/{linkTypeApiName}                - Cria relação (fromPk, toPk)
- GET    /links/{linkTypeApiName}                - Lista relações de um LinkType
- DELETE /links/{linkTypeApiName}/{fromPk}/{toPk} - Deleta relação específica
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from api.handlers.links import (
    LinkedObjectsCommandService,
    LinkedObjectsQueryService,
    get_link_admin_command_service,
    get_link_command_service,
    get_link_query_service,
)
from api.v2.schemas.bulk import LinkBulkLoadRequest
from api.v2.schemas.linked_objects import (
    LinkCreateRequest,
    LinkedObjectListResponse,
    LinkedObjectReadResponse,
)

router = APIRouter(tags=["Linked Objects"])


@router.post(
    "/links/{linkTypeApiName}",
    response_model=LinkedObjectReadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create link",
    description="Creates a relation between two object instances using a LinkType.",
)
def create_link(
    body: LinkCreateRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType"),
    command_service: LinkedObjectsCommandService = Depends(get_link_command_service),
) -> LinkedObjectReadResponse:
    return command_service.create_link(linkTypeApiName, body)


@router.get(
    "/links/{linkTypeApiName}",
    response_model=LinkedObjectListResponse,
    summary="List links by LinkType",
    description="Lists relations (edges) for the given LinkType.",
)
def list_links(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType"),
    fromPk: str | None = Query(default=None, description="Filter by source PK"),
    toPk: str | None = Query(default=None, description="Filter by target PK"),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    query_service: LinkedObjectsQueryService = Depends(get_link_query_service),
) -> LinkedObjectListResponse:
    return query_service.list_links(linkTypeApiName, from_pk=fromPk, to_pk=toPk, valid_at=validAt)


@router.delete(
    "/links/{linkTypeApiName}/{fromPk}/{toPk}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete link",
    description="Deletes a relation (edge) identified by LinkType and endpoint PKs.",
)
def delete_link(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType"),
    fromPk: str = Path(..., description="PK of the source object instance"),
    toPk: str = Path(..., description="PK of the target object instance"),
    command_service: LinkedObjectsCommandService = Depends(get_link_admin_command_service),
):
    ok = command_service.delete_link(linkTypeApiName, fromPk, toPk)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return None


@router.get(
    "/links/{linkTypeApiName}/{fromPk}/{toPk}",
    response_model=LinkedObjectReadResponse,
    summary="Get link",
    description="Returns a specific relation (edge) identified by LinkType and endpoint PKs.",
)
def get_link(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType"),
    fromPk: str = Path(..., description="PK of the source object instance"),
    toPk: str = Path(..., description="PK of the target object instance"),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    query_service: LinkedObjectsQueryService = Depends(get_link_query_service),
) -> LinkedObjectReadResponse:
    found = query_service.get_link(linkTypeApiName, fromPk, toPk, valid_at=validAt)
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return found


@router.post(
    "/links/{linkTypeApiName}/load",
    response_model=LinkedObjectListResponse,
    summary="Bulk load (create/delete) links",
    description="Create or delete multiple links in a single call.",
)
def bulk_load_links(
    body: LinkBulkLoadRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType"),
    command_service: LinkedObjectsCommandService = Depends(get_link_command_service),
) -> LinkedObjectListResponse:
    return command_service.bulk_load_links(linkTypeApiName, body)
