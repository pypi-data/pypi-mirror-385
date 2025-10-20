"""Dependency helpers for object instance command/query handlers."""

from __future__ import annotations

from fastapi import Depends
from sqlmodel import Session

from api.containers import build_instances_service
from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.dependencies import get_domain_event_bus
from api.services.instances_service import (
    ObjectInstanceCommandService,
    ObjectInstanceQueryService,
)
from ontologia.domain.events import DomainEventBus


def get_instance_command_service(
    ontologyApiName: str,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
    event_bus: DomainEventBus = Depends(get_domain_event_bus),
) -> ObjectInstanceCommandService:
    service = build_instances_service(
        session=session,
        service="ontology",
        instance=ontologyApiName,
        principal=principal,
        event_bus=event_bus,
    )
    return service.command_service


def get_instance_admin_command_service(
    ontologyApiName: str,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
    event_bus: DomainEventBus = Depends(get_domain_event_bus),
) -> ObjectInstanceCommandService:
    service = build_instances_service(
        session=session,
        service="ontology",
        instance=ontologyApiName,
        principal=principal,
        event_bus=event_bus,
    )
    return service.command_service


def get_instance_query_service(
    ontologyApiName: str,
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
    event_bus: DomainEventBus = Depends(get_domain_event_bus),
) -> ObjectInstanceQueryService:
    service = build_instances_service(
        session=session,
        service="ontology",
        instance=ontologyApiName,
        principal=principal,
        event_bus=event_bus,
    )
    return service.query_service


__all__ = [
    "ObjectInstanceCommandService",
    "ObjectInstanceQueryService",
    "get_instance_admin_command_service",
    "get_instance_command_service",
    "get_instance_query_service",
]
