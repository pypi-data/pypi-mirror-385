"""
models_sql.py
-------------
SQLModel-backed persistence models for instance layer.
Separated from public module names to allow `object_instance.py` and
`linked_object.py` to become DTOs.
"""

from __future__ import annotations

from typing import Any

from registro import ResourceTypeBaseModel
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import JSON, Column, Field


class ObjectInstance(ResourceTypeBaseModel, table=True):
    __resource_type__ = "object-instance"
    __tablename__ = "objectinstance"

    __table_args__ = (
        UniqueConstraint(
            "object_type_rid",
            "pk_value",
            name="uq_objectinstance_ot_pk",
        ),
    )

    # Referência ao tipo semântico
    object_type_api_name: str = Field(
        index=True, description="API name do ObjectType desta instância"
    )
    object_type_rid: str = Field(foreign_key="objecttype.rid", index=True)

    # Valor normalizado da PK (armazenado como string)
    pk_value: str = Field(
        index=True, description="Valor da chave primária desta instância, normalizado como string"
    )

    # Payload com propriedades desta instância
    data: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(MutableDict.as_mutable(JSON))
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"ObjectInstance(api_name='{self.api_name}', object_type='{self.object_type_api_name}', "
            f"pk_value='{self.pk_value}')"
        )


class LinkedObject(ResourceTypeBaseModel, table=True):
    __resource_type__ = "linked-object"
    __tablename__ = "linkedobject"

    __table_args__ = (
        # Unicidade por tipo de link + pares from/to
        UniqueConstraint(
            "link_type_rid",
            "from_object_rid",
            "to_object_rid",
            name="uq_linkedobject_unique",
        ),
    )

    # Referência ao LinkType semântico
    link_type_api_name: str = Field(index=True, description="API name do LinkType desta relação")
    link_type_rid: str = Field(foreign_key="linktype.rid", index=True)

    # Extremidades da relação (instâncias de objetos)
    from_object_rid: str = Field(foreign_key="objectinstance.rid", index=True)
    to_object_rid: str = Field(foreign_key="objectinstance.rid", index=True)

    # Link properties payload (edge attributes)
    data: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(MutableDict.as_mutable(JSON))
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"LinkedObject(api_name='{self.api_name}', link_type='{self.link_type_api_name}', "
            f"from='{self.from_object_rid}', to='{self.to_object_rid}')"
        )


# Late imports to avoid cycles

# Rebuild models after late imports
ObjectInstance.model_rebuild()
LinkedObject.model_rebuild()
