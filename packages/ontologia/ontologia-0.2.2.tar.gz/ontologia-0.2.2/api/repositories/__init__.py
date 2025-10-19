"""Repositories for data access."""

from api.repositories.kuzudb_repository import KuzuDBRepository, get_kuzu_repo
from api.repositories.metamodel_repository import MetamodelRepository

__all__ = ["KuzuDBRepository", "get_kuzu_repo", "MetamodelRepository"]
