"""Application-level service constructors for dependency injection."""

from __future__ import annotations

from sqlmodel import Session

from api.core.auth import UserPrincipal
from api.services.instances_service import InstancesService
from api.services.linked_objects_service import LinkedObjectsService
from ontologia.domain.events import DomainEventBus


def build_instances_service(
    *,
    session: Session,
    service: str,
    instance: str,
    principal: UserPrincipal,
    event_bus: DomainEventBus,
) -> InstancesService:
    return InstancesService(
        session,
        service=service,
        instance=instance,
        principal=principal,
        event_bus=event_bus,
    )


def build_linked_objects_service(
    *,
    session: Session,
    service: str,
    instance: str,
    principal: UserPrincipal,
    event_bus: DomainEventBus,
) -> LinkedObjectsService:
    return LinkedObjectsService(
        session,
        service=service,
        instance=instance,
        principal=principal,
        event_bus=event_bus,
    )


__all__ = [
    "build_instances_service",
    "build_linked_objects_service",
]
