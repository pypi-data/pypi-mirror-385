"""
api/v2/routers/query_types.py
-----------------------------
Endpoints REST para QueryTypes (metamodelo) e execução de queries salvas.

Endpoints:
- GET    /queryTypes                  - Lista QueryTypes
- GET    /queryTypes/{apiName}        - Busca QueryType por api_name
- PUT    /queryTypes/{apiName}        - Cria/Atualiza QueryType
- DELETE /queryTypes/{apiName}        - Deleta QueryType
- POST   /queries/{apiName}/execute   - Executa QueryType com parâmetros
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.services.metamodel_service import MetamodelService
from api.v2.schemas.instances import ObjectListResponse
from api.v2.schemas.metamodel import (
    QueryTypeListResponse,
    QueryTypePutRequest,
    QueryTypeReadResponse,
)

router = APIRouter(tags=["Query Types"])


@router.get(
    "/queryTypes",
    response_model=QueryTypeListResponse,
    summary="List all QueryTypes",
)
def list_query_types(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    *,
    includeHistorical: Annotated[
        bool,
        Query(
            description="Se verdadeiro, inclui versões anteriores dos QueryTypes",
        ),
    ] = False,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> QueryTypeListResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    return service.list_query_types(include_inactive=includeHistorical)


@router.get(
    "/queryTypes/{queryApiName}",
    response_model=QueryTypeReadResponse,
    summary="Get QueryType by API name",
)
def get_query_type(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    queryApiName: str = Path(..., description="API name of the QueryType"),
    version: int | None = Query(
        default=None,
        ge=1,
        description="Versão específica do QueryType. Se omitido, retorna a mais recente.",
    ),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> QueryTypeReadResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    qt = service.get_query_type(queryApiName, version=version)
    if not qt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QueryType not found")
    return qt


@router.put(
    "/queryTypes/{queryApiName}",
    response_model=QueryTypeReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update QueryType",
)
def upsert_query_type(
    schema: QueryTypePutRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    queryApiName: str = Path(..., description="API name of the QueryType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> QueryTypeReadResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    return service.upsert_query_type(queryApiName, schema)


@router.delete(
    "/queryTypes/{queryApiName}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete QueryType",
)
def delete_query_type(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    queryApiName: str = Path(..., description="API name of the QueryType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
):
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    ok = service.delete_query_type(queryApiName)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QueryType not found")
    return None


class QueryExecutionRequest(BaseModel):
    parameters: dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


@router.post(
    "/queries/{queryApiName}/execute",
    response_model=ObjectListResponse,
    summary="Execute a saved QueryType",
    description="Executes a QueryType using provided parameters and returns matching objects.",
)
def execute_query_type(
    body: QueryExecutionRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    queryApiName: str = Path(..., description="API name of the QueryType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> ObjectListResponse:
    service = MetamodelService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    return service.execute_query_type(
        query_api_name=queryApiName,
        parameters=dict(body.parameters or {}),
        limit=body.limit,
        offset=body.offset,
    )
