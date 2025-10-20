"""
linked_object.py
----------------
DTO (Pydantic) para relações (LinkedObject). Este módulo reexporta o DTO
para permitir a migração longe das tabelas SQLModel.
"""

from __future__ import annotations

from ontologia.domain.metamodels.instances.dtos import LinkedObjectDTO as LinkedObject

__all__ = ["LinkedObject"]
