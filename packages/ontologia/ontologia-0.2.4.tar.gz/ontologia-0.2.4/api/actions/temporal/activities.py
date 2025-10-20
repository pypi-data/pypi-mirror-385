"""
api/actions/temporal/activities.py
-----------------------------------
Temporal Activities for executing registered Actions.

This provides a generic activity `run_registered_action` that looks up an
executor by `executor_key` in `ACTION_REGISTRY` and runs it with the given
`context` and `params`.
"""

from __future__ import annotations

from typing import Any

from temporalio import activity

from api.actions.registry import ACTION_REGISTRY


@activity.defn
def run_registered_action(
    executor_key: str, context: dict[str, Any], params: dict[str, Any]
) -> dict[str, Any]:
    """Run a registered Action executor.

    The executor function must be registered in `ACTION_REGISTRY` and follow
    the signature `(context: dict, params: dict) -> dict | Any`.
    """
    func = ACTION_REGISTRY.get(executor_key)
    if not func:
        raise RuntimeError(f"Unknown executor_key: {executor_key}")

    result = func(context, params)
    return result if isinstance(result, dict) else {"status": "success", "result": result}
