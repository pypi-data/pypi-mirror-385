"""
api/v2/schemas/linked_objects.py
---------------------------------
DTOs para LinkedObjects (relações entre instâncias).
"""

from pydantic import BaseModel, ConfigDict, Field


class LinkCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    fromPk: str = Field(..., description="Valor da PK da instância de origem")
    toPk: str = Field(..., description="Valor da PK da instância de destino")
    properties: dict | None = Field(default_factory=dict, description="Propriedades do link")


class LinkedObjectReadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rid: str
    linkTypeApiName: str
    fromObjectType: str
    toObjectType: str
    fromPk: str
    toPk: str
    linkProperties: dict | None = Field(default_factory=dict)


class LinkedObjectListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data: list[LinkedObjectReadResponse] = Field(default_factory=list)
    nextPageToken: str | None = None
