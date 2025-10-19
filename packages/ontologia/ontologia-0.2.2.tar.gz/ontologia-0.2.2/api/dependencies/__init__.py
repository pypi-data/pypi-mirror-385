"""Dependency wiring for FastAPI endpoints."""

from api.dependencies.events import get_domain_event_bus
from api.dependencies.realtime import (
    ensure_runtime_started,
    get_context_provider,
    get_entity_manager,
    get_runtime,
    get_schema_registry,
    run_realtime_enricher,
    shutdown_runtime,
)

__all__ = [
    "get_domain_event_bus",
    "ensure_runtime_started",
    "get_context_provider",
    "get_entity_manager",
    "get_runtime",
    "get_schema_registry",
    "run_realtime_enricher",
    "shutdown_runtime",
]
