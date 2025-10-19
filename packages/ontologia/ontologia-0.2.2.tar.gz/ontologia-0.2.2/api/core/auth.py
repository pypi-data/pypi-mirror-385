"""
api/core/auth.py
-----------------
Security primitives for JWT-based authentication and role-aware authorization.

This module provides three core building blocks:
1. ``create_access_token`` for issuing JWT access tokens.
2. ``get_current_user`` to decode/validate tokens and yield a ``UserPrincipal``.
3. ``require_role`` dependency factory for RBAC + tenant-aware permissions.

The default implementation ships with an in-memory user registry suitable for
development/testing. In production, replace ``USERS_DB`` with calls to an
identity provider (IdP) or directory service.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any, Literal

from fastapi import Depends, Header, HTTPException, Request, status
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from api.core.settings import get_settings

ROLE_PRIORITY = {"viewer": 0, "editor": 1, "admin": 2}
TENANT_SERVICE_DEFAULT = "ontology"


class UserPrincipal(BaseModel):
    """Represents the authenticated user and their permissions."""

    user_id: str
    roles: list[str] = Field(default_factory=list)
    tenants: dict[str, str] = Field(default_factory=dict)

    def _priority(self, role: str) -> int:
        return ROLE_PRIORITY.get(role.lower(), -1)

    def has_global_role(self, required_role: str) -> bool:
        if not self.roles:
            return False
        required = self._priority(required_role)
        return any(self._priority(role) >= required for role in self.roles)

    def tenant_role(self, service: str, instance: str) -> str | None:
        key = f"{service}/{instance}"
        return self.tenants.get(key)

    def has_tenant_role(self, service: str, instance: str, required_role: str) -> bool:
        role = self.tenant_role(service, instance)
        if role is None:
            return False
        return self._priority(role) >= self._priority(required_role)

    def can(self, service: str, instance: str, required_role: str) -> bool:
        return self.has_global_role(required_role) or self.has_tenant_role(
            service, instance, required_role
        )


class UserRecord(BaseModel):
    username: str
    roles: list[str] = Field(default_factory=list)
    tenants: dict[str, str] = Field(default_factory=dict)


USERS_DB: dict[str, UserRecord] = {
    "admin": UserRecord(
        username="admin",
        roles=["admin"],
        tenants={"ontology/default": "admin"},
    ),
    "editor": UserRecord(
        username="editor",
        roles=["editor"],
        tenants={"ontology/default": "editor"},
    ),
    "viewer": UserRecord(
        username="viewer",
        roles=["viewer"],
        tenants={"ontology/default": "viewer"},
    ),
    "agent-architect-01": UserRecord(
        username="agent-architect-01",
        roles=["admin"],
        tenants={"ontology/default": "admin"},
    ),
}


class TokenPayload(BaseModel):
    sub: str
    exp: int
    roles: list[str] = Field(default_factory=list)
    tenants: dict[str, str] = Field(default_factory=dict)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105 - token type marker only


@lru_cache
def _settings_cache():
    return get_settings()


def _extract_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token.strip()


def get_user(username: str) -> UserRecord | None:
    return USERS_DB.get(username)


def authenticate_user(username: str, password: str) -> UserRecord | None:
    user = get_user(username)
    if not user or password != user.username:
        return None
    return user


def create_access_token(
    *,
    subject: str,
    roles: list[str],
    tenants: dict[str, str],
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    settings = _settings_cache()
    expire = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.jwt_access_token_ttl_minutes)
    )
    to_encode: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "roles": roles,
        "tenants": tenants,
    }
    if extra_claims:
        to_encode.update({k: v for k, v in extra_claims.items() if v is not None})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_service_account_token(
    *,
    subject: str,
    roles: list[str],
    tenants: dict[str, str],
    audience: str | None = "service-agent",
    expires_days: int = 365,
) -> str:
    """Issue a long-lived token for service-to-service authentication."""

    expires_delta = timedelta(days=expires_days)
    extra_claims: dict[str, Any] = {}
    if audience:
        extra_claims["aud"] = audience
    return create_access_token(
        subject=subject,
        roles=roles,
        tenants=tenants,
        expires_delta=expires_delta,
        extra_claims=extra_claims,
    )


async def get_current_user(token: str = Depends(_extract_bearer_token)) -> UserPrincipal:
    settings = _settings_cache()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        data = TokenPayload(**payload)
    except JWTError as exc:  # pragma: no cover - handled by HTTPException
        raise credentials_exception from exc
    return UserPrincipal(user_id=data.sub, roles=data.roles, tenants=data.tenants)


def require_role(
    required_role: str,
) -> Callable[[Request, UserPrincipal], Awaitable[UserPrincipal]]:
    """Factory that yields a dependency enforcing the required role.

    The dependency inspects both global roles and tenant-scoped permissions. The tenant is:
    - extracted from the current request's ``path_params`` (``ontologyApiName`` or ``ontology``)
    - associated with the default service "ontology" unless ``service`` is present.
    """

    async def _checker(
        request: Request,
        principal: UserPrincipal = Depends(get_current_user),
    ) -> UserPrincipal:
        service = request.path_params.get("service") or TENANT_SERVICE_DEFAULT
        instance = (
            request.path_params.get("ontologyApiName")
            or request.path_params.get("ontology")
            or request.path_params.get("tenant")
        )

        if instance:
            if not principal.can(service, instance, required_role):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        elif not principal.has_global_role(required_role):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return principal

    return _checker
