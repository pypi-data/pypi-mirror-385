"""
api/v2/routers/interfaces.py
-----------------------------
Endpoints REST para InterfaceTypes (metamodelo) – compatível com o padrão v2.

Endpoints:
- GET    /interfaces                 - Lista Interfaces
- GET    /interfaces/{apiName}       - Busca Interface por api_name
- PUT    /interfaces/{apiName}       - Cria/Atualiza Interface
- DELETE /interfaces/{apiName}       - Deleta Interface
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.services.metamodel_service import MetamodelService
from api.v2.schemas.metamodel import (
    InterfaceListResponse,
    InterfacePutRequest,
    InterfaceReadResponse,
)

router = APIRouter(tags=["Interfaces"])


@router.get(
    "/interfaces",
    response_model=InterfaceListResponse,
    summary="List all Interfaces",
    description="Returns all InterfaceTypes defined in the ontology",
)
def list_interfaces(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    *,
    includeHistorical: Annotated[
        bool,
        Query(
            description="Se verdadeiro, inclui versões anteriores das Interfaces",
        ),
    ] = False,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> InterfaceListResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    items = service.list_interface_types(include_inactive=includeHistorical)
    return items


@router.get(
    "/interfaces/{interfaceApiName}",
    response_model=InterfaceReadResponse,
    summary="Get Interface by API name",
    description="Returns a single InterfaceType by its API name",
)
def get_interface(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    interfaceApiName: str = Path(..., description="API name of the Interface"),
    version: int | None = Query(
        default=None,
        ge=1,
        description="Versão específica da Interface. Se omitido, retorna a mais recente.",
    ),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> InterfaceReadResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    itf = service.get_interface_type(interfaceApiName, version=version)
    if not itf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"InterfaceType '{interfaceApiName}' not found",
        )
    return itf


@router.put(
    "/interfaces/{interfaceApiName}",
    response_model=InterfaceReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update Interface",
    description="Creates a new InterfaceType or updates an existing one (upsert)",
)
def upsert_interface(
    schema: InterfacePutRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    interfaceApiName: str = Path(..., description="API name of the Interface"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> InterfaceReadResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    return service.upsert_interface_type(interfaceApiName, schema)


@router.delete(
    "/interfaces/{interfaceApiName}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Interface",
    description="Deletes an InterfaceType by its API name",
)
def delete_interface(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    interfaceApiName: str = Path(..., description="API name of the Interface"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
):
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    deleted = service.delete_interface_type(interfaceApiName)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"InterfaceType '{interfaceApiName}' not found",
        )
    return None
