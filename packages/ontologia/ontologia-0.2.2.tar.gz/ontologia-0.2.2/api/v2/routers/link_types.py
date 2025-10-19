"""
api/v2/routers/link_types.py
-----------------------------
Endpoints REST para LinkTypes (compatível com Foundry API).

Endpoints:
- GET    /linkTypes           - Lista todos os LinkTypes
- GET    /linkTypes/{apiName} - Busca LinkType por api_name
- PUT    /linkTypes/{apiName} - Cria ou atualiza LinkType
- DELETE /linkTypes/{apiName} - Deleta LinkType
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.services.metamodel_service import MetamodelService
from api.v2.schemas.metamodel import LinkTypeListResponse, LinkTypePutRequest, LinkTypeReadResponse

router = APIRouter(tags=["Link Types"])


@router.get(
    "/linkTypes",
    response_model=LinkTypeListResponse,
    summary="List all Link Types",
    description="Returns all LinkTypes defined in the ontology",
)
def list_link_types(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    *,
    includeHistorical: Annotated[
        bool,
        Query(
            description="Se verdadeiro, inclui versões anteriores do LinkType",
        ),
    ] = False,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> LinkTypeListResponse:
    """
    Lista todos os LinkTypes da ontologia.

    Returns:
        Lista de LinkTypes
    """
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    link_types = service.list_link_types(include_inactive=includeHistorical)

    return LinkTypeListResponse(data=link_types)


@router.get(
    "/linkTypes/{linkTypeApiName}",
    response_model=LinkTypeReadResponse,
    summary="Get Link Type by API name",
    description="Returns a single LinkType by its API name",
)
def get_link_type(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType"),
    version: int | None = Query(
        default=None,
        ge=1,
        description="Versão específica do LinkType. Se omitido, retorna a mais recente.",
    ),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> LinkTypeReadResponse:
    """
    Busca um LinkType por api_name.

    Args:
        linkTypeApiName: API name do LinkType

    Returns:
        LinkType encontrado

    Raises:
        404: Se LinkType não for encontrado
    """
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    link_type = service.get_link_type(linkTypeApiName, version=version)

    if not link_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"LinkType '{linkTypeApiName}' not found"
        )

    return link_type


@router.put(
    "/linkTypes/{linkTypeApiName}",
    response_model=LinkTypeReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update Link Type",
    description="Creates a new LinkType or updates an existing one (upsert)",
)
def upsert_link_type(
    schema: LinkTypePutRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> LinkTypeReadResponse:
    """
    Cria ou atualiza um LinkType (upsert).

    Args:
        linkTypeApiName: API name do LinkType
        schema: Dados do LinkType

    Returns:
        LinkType criado ou atualizado

    Raises:
        400: Se validações falharem
    """
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    return service.upsert_link_type(linkTypeApiName, schema)


@router.delete(
    "/linkTypes/{linkTypeApiName}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Link Type",
    description="Deletes a LinkType by its API name",
)
def delete_link_type(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
):
    """
    Deleta um LinkType por api_name.

    Args:
        linkTypeApiName: API name do LinkType

    Raises:
        404: Se LinkType não for encontrado
    """
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    deleted = service.delete_link_type(linkTypeApiName)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"LinkType '{linkTypeApiName}' not found"
        )

    # 204 No Content não retorna body
    return None
