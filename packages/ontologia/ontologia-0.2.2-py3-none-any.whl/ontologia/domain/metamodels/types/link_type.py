"""
link_type_unified.py
--------------------
Modelo de LinkType unificado, alinhado com Palantir Foundry.
Substitui o conceito de LinkTypeSide por uma relação bidirecional completa.

Key Features:
- Relação bidirecional definida atomicamente
- Cardinalidade pertence à relação (não aos "lados")
- Inverso explícito (forward + inverse)
- Alinhado com briefing do projeto (LinkType único)
"""

import enum
from datetime import datetime
from typing import Any, Optional

from pydantic import ConfigDict
from registro import ResourceTypeBaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import JSON, Column, Field, Relationship, Session, select


class Cardinality(str, enum.Enum):
    """
    Cardinalidade de uma relação entre dois ObjectTypes.
    Define a multiplicidade da relação completa (não de um lado).
    """

    ONE_TO_ONE = "ONE_TO_ONE"  # 1:1 - Um para Um
    ONE_TO_MANY = "ONE_TO_MANY"  # 1:N - Um para Muitos
    MANY_TO_ONE = "MANY_TO_ONE"  # N:1 - Muitos para Um
    MANY_TO_MANY = "MANY_TO_MANY"  # N:N - Muitos para Muitos


class LinkType(ResourceTypeBaseModel, table=True):
    """
    Representa uma relação bidirecional completa entre dois ObjectTypes.

    Inspirado no modelo do Palantir Foundry, onde um LinkType define:
    1. A direção "forward" (from -> to)
    2. A direção "inverse" (to -> from)
    3. A cardinalidade da relação como um todo

    Exemplo:
        Employee "works_for" Company (MANY_TO_ONE)
        Company "has_employees" Employee (inverso)

    Este modelo substitui LinkTypeSide, que representava apenas "metade" da relação.
    """

    __resource_type__ = "link-type"
    __tablename__ = "linktype"

    __table_args__ = (
        # Garante que não haja links duplicados entre os mesmos dois objetos
        UniqueConstraint(
            "from_object_type_api_name",
            "to_object_type_api_name",
            "api_name",
            "version",
            name="uq_linktype_complete_versioned",
        ),
        # Garante que inverse_api_name é único por versão
        UniqueConstraint(
            "inverse_api_name",
            "version",
            name="uq_linktype_inverse_api_name_versioned",
        ),
    )

    # Pydantic v2 config
    model_config = ConfigDict(
        extra="forbid", json_schema_extra={"exclude": {"from_object_type", "to_object_type"}}
    )

    # --- Cardinalidade da Relação Completa ---
    cardinality: Cardinality = Field(
        ...,
        description="Cardinalidade da relação: ONE_TO_ONE, ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY",
    )

    # --- Lado "Forward" (A -> B) ---
    # api_name herdado de ResourceTypeBaseModel (ex: "works_for")
    # display_name herdado de ResourceTypeBaseModel (ex: "Trabalha Para")

    from_object_type_api_name: str = Field(
        ..., index=True, description="API name do ObjectType de origem (lado 'from')"
    )
    to_object_type_api_name: str = Field(
        ..., index=True, description="API name do ObjectType de destino (lado 'to')"
    )

    # RIDs dos ObjectTypes (resolvidos ao validar)
    from_object_type_rid: str | None = Field(default=None, foreign_key="objecttype.rid", index=True)
    to_object_type_rid: str | None = Field(default=None, foreign_key="objecttype.rid", index=True)

    # Relacionamentos com ObjectTypes
    from_object_type: Optional["ObjectType"] = Relationship(
        back_populates="outgoing_links",
        sa_relationship_kwargs={
            "lazy": "joined",
            "foreign_keys": "[LinkType.from_object_type_rid]",
        },
    )
    to_object_type: Optional["ObjectType"] = Relationship(
        back_populates="incoming_links",
        sa_relationship_kwargs={"lazy": "joined", "foreign_keys": "[LinkType.to_object_type_rid]"},
    )

    # --- Link Properties (optional) ---
    # First-class properties that belong to the relation itself
    link_property_types: list["LinkPropertyType"] = Relationship(
        back_populates="link_type", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # --- Lado "Inverse" (B -> A) ---
    inverse_api_name: str = Field(
        ...,
        index=True,
        description="API name da relação inversa (ex: 'has_employees' se forward é 'works_for')",
    )
    inverse_display_name: str = Field(
        ..., description="Nome de exibição da relação inversa (ex: 'Empregados')"
    )

    version: int = Field(default=1, ge=1, description="Schema version", index=True)
    is_latest: bool = Field(default=True, description="Latest version flag", index=True)

    # --- Propriedades Opcionais do Link ---
    # Para links que precisam de atributos próprios
    # Ex: Um link "works_for" pode ter propriedade "since_date"
    # properties: List["PropertyType"] = Relationship(...)  # TODO: implementar

    # --- NOVO: Configuração de Fonte de Dados para Sync de Relações ---
    backing_dataset_rid: str | None = Field(
        default=None,
        foreign_key="dataset.rid",
        description="RID do Dataset que contém os dados de junção para este LinkType",
    )
    from_property_mapping: str | None = Field(
        default=None,
        description="Nome da coluna no dataset que mapeia para a PK do ObjectType de origem",
    )
    to_property_mapping: str | None = Field(
        default=None,
        description="Nome da coluna no dataset que mapeia para a PK do ObjectType de destino",
    )
    property_mappings: dict[str, str] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Mapeamento de propriedades próprias do link (coluna → propriedade)",
    )

    # Incremental sync field (APPEND) and last sync timestamp
    incremental_field: str | None = Field(
        default=None, description="Nome da coluna incremental para sync de relações (APPEND)"
    )
    last_rels_sync_time: datetime | None = Field(
        default=None, description="Última data/hora de sync de relações (para APPEND)"
    )

    # --- Constraints Opcionais ---
    max_degree_forward: int | None = Field(
        default=None, description="Máximo de links forward permitidos (opcional, para MANY)"
    )
    max_degree_inverse: int | None = Field(
        default=None, description="Máximo de links inverse permitidos (opcional, para MANY)"
    )

    def model_post_init(self, __context: Any) -> None:
        """
        Valida campos após inicialização.
        SQLModel com table=True pula validadores Pydantic durante __init__.
        """
        super().model_post_init(__context)

        # Valida que api_name é um identificador válido
        if not self.api_name or not self.api_name.isidentifier():
            raise ValueError("api_name must be a valid Python identifier")

        # Valida que api_names são identificadores válidos
        if not self.from_object_type_api_name.isidentifier():
            raise ValueError("from_object_type_api_name must be a valid Python identifier")

        if not self.to_object_type_api_name.isidentifier():
            raise ValueError("to_object_type_api_name must be a valid Python identifier")

        if not self.inverse_api_name.isidentifier():
            raise ValueError("inverse_api_name must be a valid Python identifier")

        # Valida que forward e inverse não são iguais
        if self.api_name == self.inverse_api_name:
            raise ValueError(
                f"api_name ('{self.api_name}') and inverse_api_name ('{self.inverse_api_name}') "
                "must be different"
            )

    def get_forward_definition(self) -> dict[str, Any]:
        """Retorna a definição do lado 'forward' da relação."""
        return {
            "api_name": self.api_name,
            "display_name": self.display_name,
            "from": self.from_object_type_api_name,
            "to": self.to_object_type_api_name,
            "cardinality": self._get_forward_cardinality(),
            "max_degree": self.max_degree_forward,
        }

    def get_inverse_definition(self) -> dict[str, Any]:
        """Retorna a definição do lado 'inverse' da relação."""
        return {
            "api_name": self.inverse_api_name,
            "display_name": self.inverse_display_name,
            "from": self.to_object_type_api_name,  # Invertido
            "to": self.from_object_type_api_name,  # Invertido
            "cardinality": self._get_inverse_cardinality(),
            "max_degree": self.max_degree_inverse,
        }

    def _get_forward_cardinality(self) -> str:
        """Retorna a cardinalidade do ponto de vista 'forward'."""
        mapping = {
            Cardinality.ONE_TO_ONE: "ONE",
            Cardinality.ONE_TO_MANY: "ONE",
            Cardinality.MANY_TO_ONE: "MANY",
            Cardinality.MANY_TO_MANY: "MANY",
        }
        return mapping[self.cardinality]

    def _get_inverse_cardinality(self) -> str:
        """Retorna a cardinalidade do ponto de vista 'inverse'."""
        mapping = {
            Cardinality.ONE_TO_ONE: "ONE",
            Cardinality.ONE_TO_MANY: "MANY",
            Cardinality.MANY_TO_ONE: "ONE",
            Cardinality.MANY_TO_MANY: "MANY",
        }
        return mapping[self.cardinality]

    def _get_object_type_by_api_name(self, session: Session, api_name: str) -> "ObjectType":
        """
        Busca ObjectType por api_name, com escopo de service/instance (multi-tenant).
        """
        from registro.core.resource import Resource

        stmt = (
            select(ObjectType)
            .join(Resource, Resource.rid == ObjectType.rid)
            .where(
                Resource.service == self.service,
                Resource.instance == self.instance,
                ObjectType.api_name == api_name,
            )
        )
        obj_type = session.exec(stmt).first()
        if not obj_type:
            raise ValueError(
                f"ObjectType with api_name '{api_name}' not found in "
                f"service='{self.service}', instance='{self.instance}'"
            )
        return obj_type

    def validate_and_resolve_object_types(self, session: Session) -> None:
        """
        Valida e resolve os ObjectTypes referenciados por api_name.
        Deve ser chamado após criação e antes de commit.
        """
        # Resolve ObjectType de origem
        from_obj_type = self._get_object_type_by_api_name(session, self.from_object_type_api_name)
        self.from_object_type_rid = from_obj_type.rid
        # Não atribuir relacionamento direto para evitar warnings de sessão

        # Resolve ObjectType de destino
        to_obj_type = self._get_object_type_by_api_name(session, self.to_object_type_api_name)
        self.to_object_type_rid = to_obj_type.rid
        # Não atribuir relacionamento direto para evitar warnings de sessão

        # Valida que ambos têm primary keys definidas
        self._validate_object_type_primary_key(from_obj_type)
        self._validate_object_type_primary_key(to_obj_type)

    def _validate_object_type_primary_key(self, obj_type: "ObjectType") -> None:
        """Valida que um ObjectType tem primary key configurada corretamente."""
        if not obj_type.primary_key_field:
            raise ValueError(
                f"ObjectType '{obj_type.api_name}' must have a primary_key_field defined"
            )

        primary_key_props = [p for p in obj_type.property_types if p.is_primary_key]
        if not primary_key_props:
            raise ValueError(
                f"ObjectType '{obj_type.api_name}' must have a property marked as primary key"
            )
        if len(primary_key_props) > 1:
            raise ValueError(
                f"ObjectType '{obj_type.api_name}' has multiple properties marked as primary key"
            )

        primary_key_prop = primary_key_props[0]
        if primary_key_prop.api_name != obj_type.primary_key_field:
            raise ValueError(
                f"ObjectType '{obj_type.api_name}' primary_key_field "
                f"'{obj_type.primary_key_field}' does not match primary key property "
                f"'{primary_key_prop.api_name}'"
            )

    def __repr__(self) -> str:
        return (
            f"LinkType(api_name='{self.api_name}', "
            f"from='{self.from_object_type_api_name}', "
            f"to='{self.to_object_type_api_name}', "
            f"cardinality={self.cardinality}, "
            f"inverse='{self.inverse_api_name}')"
        )


# Importações circulares no final
# Late import to avoid cycles
from ontologia.domain.metamodels.types.link_property_type import LinkPropertyType  # noqa: E402
from ontologia.domain.metamodels.types.object_type import ObjectType

LinkType.model_rebuild()
