"""
api/actions/temporal/workflows.py
----------------------------------
Temporal Workflow for executing a registered Action.

This generic workflow accepts an `executor_key`, an execution `context`, and
`params`, and delegates execution to the `run_registered_action` activity.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy

from api.actions.temporal import activities


@workflow.defn(name="ActionWorkflow")
class ActionWorkflow:
    @workflow.run
    async def run(
        self, executor_key: str, context: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        result = await workflow.execute_activity(
            activities.run_registered_action,
            args=[executor_key, context, params],
            start_to_close_timeout=timedelta(seconds=30),
            schedule_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                backoff_coefficient=2.0,
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5,
            ),
        )
        return result
