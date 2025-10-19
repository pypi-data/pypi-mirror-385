"""Temporal workflow definitions for schema migration tasks."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow

from api.migrations.temporal import activities


@workflow.defn(name="MigrationTaskWorkflow")
class MigrationTaskWorkflow:
    @workflow.run
    async def run(self, task_payload: dict[str, Any]) -> dict[str, Any]:
        plan = await workflow.execute_activity(
            activities.prepare_migration_plan,
            args=[task_payload],
            start_to_close_timeout=timedelta(seconds=30),
        )
        result = await workflow.execute_activity(
            activities.apply_migration_plan,
            args=[task_payload, plan],
            start_to_close_timeout=timedelta(minutes=5),
        )
        return result
