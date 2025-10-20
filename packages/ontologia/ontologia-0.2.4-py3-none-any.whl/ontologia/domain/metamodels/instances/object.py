"""
object.py
---------
Reexporta o DTO `ObjectInstanceDTO` como `ObjectInstance` para compatibilidade.
"""

from __future__ import annotations

from .dtos import ObjectInstanceDTO as ObjectInstance

__all__ = ["ObjectInstance"]
