"""
api/actions/registry.py
-----------------------
Simple registry for Action executors. Execution functions are registered with a
string key (executor_key) and accept signature: (context: dict, params: dict) -> dict.

Security: Only trusted code in the repository should register actions. The
ActionType stored in the DB includes metadata and the executor_key, never the
code itself.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# executor_key -> callable(context, params) -> dict
ACTION_REGISTRY: dict[str, Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]] = {}


def register_action(key: str):
    """
    Decorator to register an Action executor by key.

    Example:
        @register_action("system.log_message")
        def log_message(context, params):
            ...
    """

    def decorator(func: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]):
        if key in ACTION_REGISTRY:
            logger.warning("Action key '%s' already registered. Overwriting.", key)
        ACTION_REGISTRY[key] = func
        logger.info("Action '%s' registered.", key)
        return func

    return decorator
