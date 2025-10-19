"""
api/v2/routers/object_types.py
-------------------------------
Endpoints REST para ObjectTypes (compatível com Foundry API).

Endpoints:
- GET    /objectTypes           - Lista todos os ObjectTypes
- GET    /objectTypes/{apiName} - Busca ObjectType por api_name
- PUT    /objectTypes/{apiName} - Cria ou atualiza ObjectType
- DELETE /objectTypes/{apiName} - Deleta ObjectType
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.services.metamodel_service import MetamodelService
from api.v2.schemas.metamodel import (
    ObjectTypeListResponse,
    ObjectTypePutRequest,
    ObjectTypeReadResponse,
)

router = APIRouter(tags=["Object Types"])


@router.get(
    "/objectTypes",
    response_model=ObjectTypeListResponse,
    summary="List all Object Types",
    description="Returns all ObjectTypes defined in the ontology",
)
def list_object_types(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    *,
    includeHistorical: Annotated[
        bool,
        Query(
            description="Se verdadeiro, inclui todas as versões (não apenas a mais recente)",
        ),
    ] = False,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> ObjectTypeListResponse:
    """
    Lista todos os ObjectTypes da ontologia.

    Returns:
        Lista de ObjectTypes
    """
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    object_types = service.list_object_types(include_inactive=includeHistorical)

    return ObjectTypeListResponse(data=object_types)


@router.get(
    "/objectTypes/{objectTypeApiName}",
    response_model=ObjectTypeReadResponse,
    summary="Get Object Type by API name",
    description="Returns a single ObjectType by its API name",
)
def get_object_type(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    version: int | None = Query(
        default=None,
        ge=1,
        description="Versão específica do ObjectType. Se omitido, retorna a mais recente.",
    ),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> ObjectTypeReadResponse:
    """
    Busca um ObjectType por api_name.

    Args:
        objectTypeApiName: API name do ObjectType

    Returns:
        ObjectType encontrado

    Raises:
        404: Se ObjectType não for encontrado
    """
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    object_type = service.get_object_type(objectTypeApiName, version=version)

    if not object_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ObjectType '{objectTypeApiName}' not found",
        )

    return object_type


@router.put(
    "/objectTypes/{objectTypeApiName}",
    response_model=ObjectTypeReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update Object Type",
    description="Creates a new ObjectType or updates an existing one (upsert)",
)
def upsert_object_type(
    schema: ObjectTypePutRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> ObjectTypeReadResponse:
    """
    Cria ou atualiza um ObjectType (upsert).

    Args:
        objectTypeApiName: API name do ObjectType
        schema: Dados do ObjectType

    Returns:
        ObjectType criado ou atualizado

    Raises:
        400: Se validações falharem
    """
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    return service.upsert_object_type(objectTypeApiName, schema)


@router.delete(
    "/objectTypes/{objectTypeApiName}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Object Type",
    description="Deletes an ObjectType by its API name",
)
def delete_object_type(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
):
    """
    Deleta um ObjectType por api_name.

    Args:
        objectTypeApiName: API name do ObjectType

    Raises:
        404: Se ObjectType não for encontrado
    """
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    deleted = service.delete_object_type(objectTypeApiName)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ObjectType '{objectTypeApiName}' not found",
        )

    # 204 No Content não retorna body
    return None
