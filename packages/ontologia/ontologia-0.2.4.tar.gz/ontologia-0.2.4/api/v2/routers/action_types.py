"""
api/v2/routers/action_types.py
------------------------------
Endpoints REST para ActionTypes (metamodelo) – compatível com o padrão v2.

Endpoints:
- GET    /actionTypes                 - Lista ActionTypes
- GET    /actionTypes/{apiName}       - Busca ActionType por api_name
- PUT    /actionTypes/{apiName}       - Cria/Atualiza ActionType
- DELETE /actionTypes/{apiName}       - Deleta ActionType
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.services.metamodel_service import MetamodelService
from api.v2.schemas.metamodel import (
    ActionTypeListResponse,
    ActionTypePutRequest,
    ActionTypeReadResponse,
)

router = APIRouter(tags=["Action Types"])


@router.get(
    "/actionTypes",
    response_model=ActionTypeListResponse,
    summary="List all ActionTypes",
    description="Returns all ActionTypes defined in the ontology",
)
def list_action_types(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    *,
    includeHistorical: Annotated[
        bool,
        Query(
            description="Se verdadeiro, inclui versões anteriores dos ActionTypes",
        ),
    ] = False,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> ActionTypeListResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    items = service.list_action_types(include_inactive=includeHistorical)
    return items


@router.get(
    "/actionTypes/{actionApiName}",
    response_model=ActionTypeReadResponse,
    summary="Get ActionType by API name",
    description="Returns a single ActionType by its API name",
)
def get_action_type(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    actionApiName: str = Path(..., description="API name of the ActionType"),
    version: int | None = Query(
        default=None,
        ge=1,
        description="Versão específica do ActionType. Se omitido, retorna a mais recente.",
    ),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> ActionTypeReadResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    act = service.get_action_type(actionApiName, version=version)
    if not act:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ActionType '{actionApiName}' not found",
        )
    return act


@router.put(
    "/actionTypes/{actionApiName}",
    response_model=ActionTypeReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update ActionType",
    description="Creates a new ActionType or updates an existing one (upsert)",
)
def upsert_action_type(
    schema: ActionTypePutRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    actionApiName: str = Path(..., description="API name of the ActionType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> ActionTypeReadResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    return service.upsert_action_type(actionApiName, schema)


@router.delete(
    "/actionTypes/{actionApiName}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete ActionType",
    description="Deletes an ActionType by its API name",
)
def delete_action_type(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    actionApiName: str = Path(..., description="API name of the ActionType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
):
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    deleted = service.delete_action_type(actionApiName)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ActionType '{actionApiName}' not found",
        )
    return None
