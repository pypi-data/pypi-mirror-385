"""
Run a Temporal Worker for Actions.

Starts a worker on the task queue `actions` that hosts:
- Workflow: ActionWorkflow
- Activities: run_registered_action

Usage:
  uv run python scripts/run_temporal_worker.py

Environment:
  TEMPORAL_ADDRESS   (default: 127.0.0.1:7233)
  TEMPORAL_NAMESPACE (default: default)
  TEMPORAL_TASK_QUEUE (default: actions)
"""

from __future__ import annotations

import asyncio

from temporalio.worker import Worker

from api.actions.temporal.activities import run_registered_action
from api.actions.temporal.workflows import ActionWorkflow
from api.core.settings import get_settings
from api.core.temporal import connect_temporal
from api.migrations.temporal.activities import (
    apply_migration_plan,
    prepare_migration_plan,
)
from api.migrations.temporal.workflows import MigrationTaskWorkflow


async def main() -> None:
    settings = get_settings()
    client = await connect_temporal(settings)
    task_queue = settings.temporal_task_queue
    print(
        "Starting Temporal worker at "
        f"{settings.temporal_address} (ns={settings.temporal_namespace}) on queue '{task_queue}'…"
    )
    async with Worker(
        client,
        task_queue=task_queue,
        workflows=[ActionWorkflow, MigrationTaskWorkflow],
        activities=[run_registered_action, prepare_migration_plan, apply_migration_plan],
    ):
        print("Worker running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
