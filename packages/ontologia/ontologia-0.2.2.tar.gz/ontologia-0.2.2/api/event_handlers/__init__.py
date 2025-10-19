"""Application-level domain event handlers."""

from __future__ import annotations

from .graph import register_graph_event_handlers

__all__ = ["register_graph_event_handlers"]
