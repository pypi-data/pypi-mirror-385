"""Dependency helpers for link command/query handlers."""

from __future__ import annotations

from fastapi import Depends
from sqlmodel import Session

from api.containers import build_linked_objects_service
from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.dependencies import get_domain_event_bus
from api.services.linked_objects_service import (
    LinkedObjectsCommandService,
    LinkedObjectsQueryService,
)
from ontologia.domain.events import DomainEventBus


def get_link_command_service(
    ontologyApiName: str,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
    event_bus: DomainEventBus = Depends(get_domain_event_bus),
) -> LinkedObjectsCommandService:
    service = build_linked_objects_service(
        session=session,
        service="ontology",
        instance=ontologyApiName,
        principal=principal,
        event_bus=event_bus,
    )
    return service.command_service


def get_link_admin_command_service(
    ontologyApiName: str,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
    event_bus: DomainEventBus = Depends(get_domain_event_bus),
) -> LinkedObjectsCommandService:
    service = build_linked_objects_service(
        session=session,
        service="ontology",
        instance=ontologyApiName,
        principal=principal,
        event_bus=event_bus,
    )
    return service.command_service


def get_link_query_service(
    ontologyApiName: str,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
    event_bus: DomainEventBus = Depends(get_domain_event_bus),
) -> LinkedObjectsQueryService:
    service = build_linked_objects_service(
        session=session,
        service="ontology",
        instance=ontologyApiName,
        principal=principal,
        event_bus=event_bus,
    )
    return service.query_service


__all__ = [
    "LinkedObjectsCommandService",
    "LinkedObjectsQueryService",
    "get_link_admin_command_service",
    "get_link_command_service",
    "get_link_query_service",
]
