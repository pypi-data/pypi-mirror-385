"""Pydantic schemas (DTOs) for API v2."""

from api.v2.schemas.metamodel import (
    InterfaceListResponse,
    InterfacePutRequest,
    InterfaceReadResponse,
    LinkInverseDefinition,
    LinkTypeListResponse,
    LinkTypePutRequest,
    LinkTypeReadResponse,
    ObjectTypeListResponse,
    ObjectTypePutRequest,
    ObjectTypeReadResponse,
    PropertyDefinition,
)

__all__ = [
    "PropertyDefinition",
    "ObjectTypePutRequest",
    "ObjectTypeReadResponse",
    "ObjectTypeListResponse",
    "LinkInverseDefinition",
    "LinkTypePutRequest",
    "LinkTypeReadResponse",
    "LinkTypeListResponse",
    "InterfacePutRequest",
    "InterfaceReadResponse",
    "InterfaceListResponse",
]
