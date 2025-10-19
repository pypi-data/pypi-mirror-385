"""
object_instance.py
-------------------
DTO (Pydantic) para instâncias de ObjectType. Este módulo reexporta o DTO
para permitir a migração longe das tabelas SQLModel.
"""

from __future__ import annotations

from ontologia.domain.metamodels.instances.dtos import ObjectInstanceDTO as ObjectInstance

__all__ = ["ObjectInstance"]
