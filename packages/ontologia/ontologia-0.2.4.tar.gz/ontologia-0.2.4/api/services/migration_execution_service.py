"""Helpers for executing schema migration tasks against instance data."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

from fastapi import HTTPException
from sqlmodel import Session, select

from ontologia.domain.instances.repositories import ObjectInstanceRepository
from ontologia.domain.metamodel.aggregates import ObjectTypeAggregate
from ontologia.domain.metamodel.repositories import (
    MetamodelRepository as MetamodelRepositoryProtocol,
)
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.domain.metamodels.migrations.migration_task import (
    MigrationTask,
    MigrationTaskStatus,
)
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.infrastructure.persistence.sql.instances_repository import (
    SQLObjectInstanceRepository,
)
from ontologia.infrastructure.persistence.sql.metamodel_repository import (
    SQLMetamodelRepository,
)

logger = logging.getLogger(__name__)


class MigrationExecutionService:
    """Execute destructive schema migration tasks produced by SchemaEvolutionService."""

    def __init__(
        self,
        session: Session,
        metamodel_repo: MetamodelRepositoryProtocol | None = None,
        instances_repo: ObjectInstanceRepository | None = None,
    ):
        self.session = session
        self.metamodel_repo = metamodel_repo or SQLMetamodelRepository(session)
        self.instances_repo = instances_repo or SQLObjectInstanceRepository(session)

    # ------------------------------------------------------------------
    # Public API

    def run_task(
        self,
        service: str,
        instance: str,
        task_rid: str,
        *,
        dry_run: bool = False,
        batch_size: int | None = None,
    ) -> dict[str, Any]:
        """Execute a single migration task, optionally as a dry run."""

        task = self.session.get(MigrationTask, task_rid)
        if not task or not self._matches_tenant(task, service, instance):
            raise ValueError(f"MigrationTask '{task_rid}' not found for {service}/{instance}")

        if not dry_run and task.status == MigrationTaskStatus.RUNNING:
            raise ValueError(f"MigrationTask '{task_rid}' is already running")

        object_type = self.metamodel_repo.get_object_type_by_api_name(
            service,
            instance,
            task.object_type_api_name,
        )
        if not object_type:
            raise ValueError(
                f"ObjectType '{task.object_type_api_name}' not found for {service}/{instance}"
            )

        operations = list((task.plan or {}).get("operations", []))
        batch = max(1, batch_size or 500)

        total = 0
        failed_messages: list[str] = []

        aggregate = ObjectTypeAggregate.from_model(object_type)

        instances_iter = self._iterate_instances(service, instance, object_type.api_name, batch)
        total, failed_messages = self._validate_instances(aggregate, instances_iter)

        if dry_run:
            return self._build_result(
                task,
                dry_run=True,
                total=total,
                failures=failed_messages,
                operations=len(operations),
                updated=total - len(failed_messages),
            )

        task.status = MigrationTaskStatus.RUNNING
        task.error_message = None
        self.session.add(task)
        self.session.commit()

        if failed_messages:
            task.status = MigrationTaskStatus.FAILED
            task.error_message = failed_messages[0][:500]
            self.session.add(task)
            self.session.commit()
            logger.warning(
                "migration_task.failed task=%s service=%s instance=%s failures=%d",
                task_rid,
                service,
                instance,
                len(failed_messages),
            )
            return self._build_result(
                task,
                dry_run=False,
                total=total,
                failures=failed_messages,
                operations=len(operations),
                updated=0,
            )

        # Second pass applies normalized payloads (guaranteed to succeed after validation)
        applied = 0
        for inst in self._iterate_instances(service, instance, object_type.api_name, batch):
            normalized = aggregate.normalize_instance_properties(
                inst.pk_value,
                self._sanitize_properties(inst, aggregate.object_type),
            )
            inst.data = normalized
            inst.display_name = f"{object_type.api_name}:{inst.pk_value}"
            applied += 1

        task.status = MigrationTaskStatus.COMPLETED
        task.error_message = None
        self.session.add(task)
        self.session.commit()

        logger.info(
            "migration_task.completed task=%s service=%s instance=%s processed=%d",
            task_rid,
            service,
            instance,
            applied,
        )

        return self._build_result(
            task,
            dry_run=False,
            total=total,
            failures=[],
            operations=len(operations),
            updated=applied,
        )

    def run_pending_tasks(
        self,
        service: str,
        instance: str,
        *,
        dry_run: bool = False,
        limit: int | None = None,
        batch_size: int | None = None,
    ) -> list[dict[str, Any]]:
        """Run all pending migration tasks for the given tenant."""

        stmt = select(MigrationTask)
        tasks = [
            task
            for task in self.session.exec(stmt).all()
            if task.status == MigrationTaskStatus.PENDING
            and self._matches_tenant(task, service, instance)
        ]
        if limit is not None:
            tasks = tasks[: max(0, limit)]

        results: list[dict[str, Any]] = []
        for task in tasks:
            results.append(
                self.run_task(
                    service,
                    instance,
                    task.rid,
                    dry_run=dry_run,
                    batch_size=batch_size,
                )
            )
        return results

    # ------------------------------------------------------------------
    # Helpers

    def _iterate_instances(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        batch_size: int,
    ) -> Iterable[ObjectInstance]:
        offset = 0
        while True:
            batch = self.instances_repo.list_object_instances(
                service,
                instance,
                object_type_api_name=object_type_api_name,
                limit=batch_size,
                offset=offset,
            )
            if not batch:
                break
            yield from batch
            if len(batch) < batch_size:
                break
            offset += batch_size

    def _validate_instances(
        self,
        aggregate: ObjectTypeAggregate,
        instances: Iterable[ObjectInstance],
    ) -> tuple[int, list[str]]:
        total = 0
        failures: list[str] = []
        for inst in instances:
            total += 1
            try:
                aggregate.normalize_instance_properties(
                    inst.pk_value,
                    self._sanitize_properties(inst, aggregate.object_type),
                )
            except HTTPException as exc:
                failures.append(f"{inst.pk_value}: {exc.detail}")
            except Exception as exc:  # pragma: no cover - defensive
                failures.append(f"{inst.pk_value}: {exc}")
        return total, failures

    def _sanitize_properties(self, inst: ObjectInstance, object_type: ObjectType) -> dict[str, Any]:
        allowed = {prop.api_name for prop in object_type.property_types}
        pk_field = object_type.primary_key_field
        sanitized: dict[str, Any] = {}
        payload = dict(inst.data or {})
        for name, value in payload.items():
            if name == pk_field:
                continue
            if name in allowed:
                sanitized[name] = value
        return sanitized

    def _build_result(
        self,
        task: MigrationTask,
        *,
        dry_run: bool,
        total: int,
        failures: list[str],
        operations: int,
        updated: int,
    ) -> dict[str, Any]:
        status_value = task.status.value if not dry_run else task.status.value
        return {
            "taskRid": task.rid,
            "objectTypeApiName": task.object_type_api_name,
            "dryRun": dry_run,
            "totalInstances": total,
            "updatedCount": updated,
            "failedCount": len(failures),
            "errors": failures[:50],
            "operationsPlanned": operations,
            "taskStatus": status_value,
        }

    def _matches_tenant(self, task: MigrationTask, service: str, instance: str) -> bool:
        return (
            getattr(task, "service", service) == service
            and getattr(task, "instance", instance) == instance
        )
