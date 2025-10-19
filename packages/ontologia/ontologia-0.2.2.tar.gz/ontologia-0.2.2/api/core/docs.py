"""Centralized OpenAPI metadata, tags, and reusable schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiError(BaseModel):
    """Canonical error payload returned by the Ontology API."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {"detail": "ObjectType 'employee' not found", "code": "object_type_not_found"}
            ]
        },
    )

    detail: str = Field(
        ...,
        description="Human-readable message describing why the request failed.",
        examples=["ObjectType 'employee' not found"],
    )
    code: str | None = Field(
        None,
        description="Stable, machine-friendly error identifier.",
        examples=["object_type_not_found"],
    )
    more_info: str | None = Field(
        None,
        description="Optional URL with remediation guidance or additional documentation.",
        alias="moreInfo",
        serialization_alias="moreInfo",
        examples=["https://ontologia.dev/docs/errors#object-type-not-found"],
    )


API_TAGS: list[dict[str, Any]] = [
    {
        "name": "Object Types",
        "description": (
            "Create, read, update, and delete metamodel ObjectTypes that define the structure "
            "of your ontology."
        ),
    },
    {
        "name": "Link Types",
        "description": "Manage relationship schemas that connect ObjectTypes together.",
    },
    {
        "name": "Actions",
        "description": (
            "Discover and invoke actions, whether executed synchronously or orchestrated via Temporal."
        ),
    },
    {
        "name": "Objects",
        "description": (
            "Work with instance data, including filtered search, aggregation, traversal, and bulk operations."
        ),
    },
    {
        "name": "Datasets",
        "description": "Inspect dataset definitions, branches, and transactions powering ingestion pipelines.",
    },
    {
        "name": "Interfaces",
        "description": "Model polymorphic contracts that unify multiple ObjectTypes under a shared interface.",
    },
    {
        "name": "Analytics",
        "description": "Run aggregate queries across object instances with familiar metrics and groupings.",
    },
    {
        "name": "Query Types",
        "description": "Define and execute saved queries that encapsulate complex business logic.",
    },
    {
        "name": "Auth",
        "description": "Obtain JWT access tokens for authenticated API usage.",
    },
]


SWAGGER_UI_PARAMETERS: dict[str, Any] = {
    "docExpansion": "list",
    "deepLinking": True,
    "displayRequestDuration": True,
    "syntaxHighlight": {"activated": True, "theme": "obsidian"},
}


SERVERS_METADATA = [
    {"url": "http://localhost:8000", "description": "Local development"},
    {"url": "https://api.ontologia.example", "description": "Reference deployment"},
]


SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": (
            "Paste a JWT access token obtained via `/v2/auth/token`. Tokens encapsulate global and "
            "tenant-scoped roles used for RBAC enforcement."
        ),
    }
}


DEFAULT_ERROR_COMPONENTS = {
    "responses": {
        "UnauthorizedError": {
            "description": "Authentication credentials were missing or invalid.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "example": {
                        "detail": "Missing Authorization header",
                        "code": "auth_header_missing",
                    },
                }
            },
        },
        "ForbiddenError": {
            "description": "The provided credentials are valid but do not grant access to the resource.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "example": {
                        "detail": "Forbidden",
                        "code": "forbidden",
                    },
                }
            },
        },
        "TooManyRequestsError": {
            "description": "Rate limit exceeded. Retry after the indicated time window.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "example": {
                        "detail": "Too many requests",
                        "code": "rate_limit_exceeded",
                    },
                }
            },
        },
        "ServerError": {
            "description": "Unexpected error encountered while processing the request.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "example": {
                        "detail": "Internal server error",
                        "code": "internal_error",
                    },
                }
            },
        },
    }
}


def api_error_schema() -> dict[str, Any]:
    """Return the JSON schema for :class:`ApiError` with proper OpenAPI refs."""

    return ApiError.model_json_schema(ref_template="#/components/schemas/{model}")
