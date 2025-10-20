"""
api/actions/test_actions.py
---------------------------
Example Action implementations for smoke testing the Actions framework.
"""

from __future__ import annotations

from typing import Any

from api.actions.registry import register_action


@register_action("system.log_message")
def log_message(context: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """
    Minimal action that logs/echoes a message with optional target info.

    Params:
      - message: string (required)
    """
    msg = params.get("message")
    if not isinstance(msg, str) or not msg:
        raise ValueError("'message' parameter must be a non-empty string")

    target = context.get("target_object")
    target_ref = None
    if target is not None:
        try:
            target_ref = f"{target.object_type_api_name}:{target.pk_value}"
        except Exception:
            target_ref = None

    return {
        "status": "success",
        "message": msg,
        "target": target_ref,
    }
