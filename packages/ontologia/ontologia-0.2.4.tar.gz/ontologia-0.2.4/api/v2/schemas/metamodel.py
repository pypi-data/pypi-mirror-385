"""
api/v2/schemas/metamodel.py
----------------------------
DTOs (Data Transfer Objects) Pydantic para a API v2 de Metadados.

Estes schemas definem o contrato da API e são compatíveis com a
API do Palantir Foundry Ontology.

Referências:
- Foundry Ontology API: /v2/ontologies/{ontologyApiName}/objectTypes
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from api.v2.schemas.actions import ActionParameterDefinition

# --- Property Definitions ---


class PropertyDefinition(BaseModel):
    """
    Define uma propriedade de um ObjectType.

    Foundry-compatible.
    """

    model_config = ConfigDict(populate_by_name=True)

    dataType: Literal["string", "integer", "double", "boolean", "date", "timestamp"] = Field(
        ..., description="Tipo de dado da propriedade"
    )
    displayName: str = Field(..., description="Nome legível da propriedade")
    description: str | None = Field(default=None, description="Descrição da propriedade")
    required: bool | None = Field(default=False, description="Se a propriedade é obrigatória")
    qualityChecks: list[str] | None = Field(
        default=None,
        description="Regras de qualidade de dados (ex: 'not_null', 'in[...]', 'between[...]')",
    )
    derivationScript: str | None = Field(
        default=None,
        description="Expressão derivada (segura) avaliada em leituras para calcular o valor dinamicamente",
    )


# --- Object Type Schemas ---


class ObjectTypePutRequest(BaseModel):
    """
    Request body para PUT /v2/ontologies/{ontologyApiName}/objectTypes/{objectTypeApiName}

    Foundry-compatible.
    """

    model_config = ConfigDict(populate_by_name=True)

    displayName: str = Field(..., description="Nome legível do ObjectType")
    description: str | None = Field(default=None, description="Descrição do ObjectType")
    primaryKey: str = Field(
        ..., description="Nome da propriedade que é a chave primária", alias="primaryKey"
    )
    properties: dict[str, PropertyDefinition] = Field(
        ..., description="Dicionário de propriedades (api_name → definition)"
    )
    implements: list[str] = Field(
        default_factory=list,
        description="Lista de API names de Interfaces que este ObjectType implementa",
    )


class ObjectTypeReadResponse(BaseModel):
    """
    Response body para GET /v2/ontologies/{ontologyApiName}/objectTypes/{objectTypeApiName}

    Foundry-compatible.
    """

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    apiName: str = Field(..., description="API name único do ObjectType")
    rid: str = Field(..., description="Resource Identifier único")
    version: int = Field(..., ge=1, description="Versão do metamodelo")
    isLatest: bool = Field(..., description="Indica se esta versão é a mais recente")
    displayName: str
    description: str | None = None
    primaryKey: str
    properties: dict[str, PropertyDefinition]
    implements: list[str] = Field(
        default_factory=list, description="Lista de Interfaces implementadas (api names)"
    )


# --- Interface Schemas ---


class InterfacePutRequest(BaseModel):
    """
    Request body para PUT /v2/ontologies/{ontologyApiName}/interfaces/{interfaceApiName}
    """

    model_config = ConfigDict(populate_by_name=True)

    displayName: str = Field(..., description="Nome legível da Interface")
    description: str | None = Field(default=None, description="Descrição")
    properties: dict[str, dict] | None = Field(
        default_factory=dict, description="Contrato de propriedades da Interface (opcional)"
    )


class InterfaceReadResponse(BaseModel):
    """
    Response body para GET /v2/ontologies/{ontologyApiName}/interfaces/{interfaceApiName}
    """

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    apiName: str = Field(..., description="API name único da Interface")
    rid: str = Field(..., description="Resource Identifier único")
    version: int = Field(..., ge=1, description="Versão do metamodelo")
    isLatest: bool = Field(..., description="Indica se esta versão é a mais recente")
    displayName: str
    description: str | None = None
    properties: dict[str, dict] | None = Field(default_factory=dict)


class InterfaceListResponse(BaseModel):
    """Response para listagem de Interfaces."""

    model_config = ConfigDict(populate_by_name=True)

    data: list[InterfaceReadResponse] = Field(
        default_factory=list, description="Lista de Interfaces"
    )
    nextPageToken: str | None = Field(
        default=None, description="Token para próxima página (paginação futura)"
    )


# --- Action Type Schemas ---


class RuleDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    description: str
    ruleLogic: str = Field(..., alias="ruleLogic")


class ActionTypePutRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    displayName: str
    description: str | None = None
    targetObjectType: str
    parameters: dict[str, ActionParameterDefinition] = Field(default_factory=dict)
    submissionCriteria: list[RuleDefinition] = Field(default_factory=list)
    validationRules: list[RuleDefinition] = Field(default_factory=list)
    executorKey: str


class ActionTypeReadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    apiName: str
    rid: str
    version: int = Field(..., ge=1, description="Versão do metamodelo")
    isLatest: bool = Field(..., description="Indica se esta versão é a mais recente")
    displayName: str
    description: str | None = None
    targetObjectType: str
    parameters: dict[str, ActionParameterDefinition] = Field(default_factory=dict)
    submissionCriteria: list[RuleDefinition] = Field(default_factory=list)
    validationRules: list[RuleDefinition] = Field(default_factory=list)
    executorKey: str


class ActionTypeListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data: list[ActionTypeReadResponse] = Field(default_factory=list)
    nextPageToken: str | None = None


# --- Link Type Schemas ---


class LinkInverseDefinition(BaseModel):
    """
    Define a direção inversa de um LinkType.

    Foundry-compatible.
    """

    model_config = ConfigDict(populate_by_name=True)

    apiName: str = Field(..., description="API name da relação inversa", alias="apiName")
    displayName: str = Field(..., description="Nome legível da relação inversa")


class LinkTypePutRequest(BaseModel):
    """
    Request body para PUT /v2/ontologies/{ontologyApiName}/linkTypes/{linkTypeApiName}

    Foundry-compatible.
    """

    model_config = ConfigDict(populate_by_name=True)

    displayName: str = Field(..., description="Nome legível do LinkType (direção forward)")
    cardinality: Literal["ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_ONE", "MANY_TO_MANY"] = Field(
        ..., description="Cardinalidade da relação"
    )
    fromObjectType: str = Field(..., description="API name do ObjectType de origem")
    toObjectType: str = Field(..., description="API name do ObjectType de destino")
    inverse: LinkInverseDefinition = Field(..., description="Definição da relação inversa")
    description: str | None = Field(default=None, description="Descrição do LinkType")
    # Optional set of link properties (edge attributes)
    properties: dict[str, PropertyDefinition] | None = Field(
        default_factory=dict, description="Propriedades pertencentes ao LinkType (edge)"
    )

    # Optional backing dataset and column mappings for sync
    backingDatasetApiName: str | None = Field(
        default=None, description="API name do Dataset de junção que abastece este LinkType"
    )
    fromPropertyMapping: str | None = Field(
        default=None,
        description="Nome da coluna no dataset que mapeia para a PK do ObjectType de origem",
    )
    toPropertyMapping: str | None = Field(
        default=None,
        description="Nome da coluna no dataset que mapeia para a PK do ObjectType de destino",
    )
    propertyMappings: dict[str, str] | None = Field(
        default=None, description="Mapeamentos de propriedades do link (coluna → propriedade)"
    )
    # Optional incremental sync field for APPEND mode on relation dataset
    incrementalField: str | None = Field(
        default=None, description="Nome da coluna incremental para sync de relações (APPEND)"
    )


class LinkTypeReadResponse(BaseModel):
    """
    Response body para GET /v2/ontologies/{ontologyApiName}/linkTypes/{linkTypeApiName}

    Foundry-compatible.
    """

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    apiName: str = Field(..., description="API name único do LinkType")
    rid: str = Field(..., description="Resource Identifier único")
    version: int = Field(..., ge=1, description="Versão do metamodelo")
    isLatest: bool = Field(..., description="Indica se esta versão é a mais recente")
    displayName: str
    cardinality: Literal["ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_ONE", "MANY_TO_MANY"]
    fromObjectType: str
    toObjectType: str
    inverse: LinkInverseDefinition
    description: str | None = None
    properties: dict[str, PropertyDefinition] | None = Field(
        default_factory=dict, description="Propriedades pertencentes ao LinkType (edge)"
    )


# --- List Responses ---


class ObjectTypeListResponse(BaseModel):
    """Response para listagem de ObjectTypes."""

    model_config = ConfigDict(populate_by_name=True)

    data: list[ObjectTypeReadResponse] = Field(
        default_factory=list, description="Lista de ObjectTypes"
    )
    nextPageToken: str | None = Field(
        default=None, description="Token para próxima página (paginação futura)"
    )


class LinkTypeListResponse(BaseModel):
    """Response para listagem de LinkTypes."""

    model_config = ConfigDict(populate_by_name=True)

    data: list[LinkTypeReadResponse] = Field(default_factory=list, description="Lista de LinkTypes")
    nextPageToken: str | None = Field(
        default=None, description="Token para próxima página (paginação futura)"
    )


# --- Query Type Schemas ---


class QueryTypePutRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    displayName: str
    description: str | None = None
    # Foundry SDK uses 'targetApiName'; keep 'targetObjectType' for back-compat
    targetObjectType: str | None = None
    targetApiName: str | None = None
    # Reuse ActionParameterDefinition shape for uniformity
    parameters: dict[str, ActionParameterDefinition] = Field(default_factory=dict)
    # Store search templates using existing search schema shapes
    whereTemplate: list[dict] = Field(default_factory=list)
    orderByTemplate: list[dict] = Field(default_factory=list)
    # Alias: unified query object { where, orderBy }
    query: dict | None = None


class QueryTypeReadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    apiName: str
    rid: str
    version: int = Field(..., ge=1, description="Versão do metamodelo")
    isLatest: bool = Field(..., description="Indica se esta versão é a mais recente")
    displayName: str
    description: str | None = None
    targetObjectType: str
    # Also surface targetApiName for SDK parity
    targetApiName: str | None = None
    parameters: dict[str, ActionParameterDefinition] = Field(default_factory=dict)
    whereTemplate: list[dict] = Field(default_factory=list)
    orderByTemplate: list[dict] = Field(default_factory=list)
    # Also include combined query for convenience
    query: dict | None = None


class QueryTypeListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data: list[QueryTypeReadResponse] = Field(default_factory=list)
    nextPageToken: str | None = None
