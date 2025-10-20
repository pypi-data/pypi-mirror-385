"""
api/v2/schemas/instances.py
----------------------------
DTOs (Pydantic) para a API v2 de Instâncias (Objects).
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ObjectUpsertRequest(BaseModel):
    """
    Request body para PUT /v2/ontologies/{ontologyApiName}/objects/{objectTypeApiName}/{pk}
    """

    model_config = ConfigDict(populate_by_name=True)

    properties: dict[str, Any] = Field(default_factory=dict, description="Mapa propriedade → valor")


class ObjectReadResponse(BaseModel):
    """
    Resposta para GET/PUT de uma instância de objeto.
    """

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    rid: str = Field(..., description="RID da instância")
    objectTypeApiName: str = Field(..., description="API name do ObjectType")
    pkValue: str = Field(..., description="Valor da PK (normalizado)")
    properties: dict[str, Any] = Field(default_factory=dict)


class ObjectListResponse(BaseModel):
    """
    Resposta de listagem de instâncias.
    """

    model_config = ConfigDict(populate_by_name=True)

    data: list[ObjectReadResponse] = Field(default_factory=list)
    nextPageToken: str | None = None
