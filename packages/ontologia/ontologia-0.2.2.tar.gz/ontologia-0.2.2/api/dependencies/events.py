"""FastAPI dependency helpers for domain event bus wiring."""

from __future__ import annotations

from functools import lru_cache

from api.event_handlers import register_graph_event_handlers
from ontologia.domain.events import DomainEventBus, InProcessEventBus


@lru_cache(maxsize=1)
def _shared_event_bus() -> InProcessEventBus:
    bus = InProcessEventBus()
    register_graph_event_handlers(bus)
    return bus


def get_domain_event_bus() -> DomainEventBus:
    """Return the application-level event bus instance."""

    return _shared_event_bus()
