"""FastAPI routers for API v2."""

from api.v2.routers import (
    action_types,
    actions,
    datasets,
    interfaces,
    link_types,
    linked_objects,
    object_types,
    objects,
    query_types,
    realtime,
)

__all__ = [
    "object_types",
    "link_types",
    "objects",
    "linked_objects",
    "interfaces",
    "actions",
    "action_types",
    "datasets",
    "realtime",
    "query_types",
]
