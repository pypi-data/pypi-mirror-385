"""Application-level command/query dependency helpers."""

from __future__ import annotations

from .instances import (
    ObjectInstanceCommandService,
    ObjectInstanceQueryService,
    get_instance_admin_command_service,
    get_instance_command_service,
    get_instance_query_service,
)
from .links import (
    LinkedObjectsCommandService,
    LinkedObjectsQueryService,
    get_link_admin_command_service,
    get_link_command_service,
    get_link_query_service,
)

__all__ = [
    "ObjectInstanceCommandService",
    "ObjectInstanceQueryService",
    "LinkedObjectsCommandService",
    "LinkedObjectsQueryService",
    "get_instance_admin_command_service",
    "get_instance_command_service",
    "get_instance_query_service",
    "get_link_admin_command_service",
    "get_link_command_service",
    "get_link_query_service",
]
