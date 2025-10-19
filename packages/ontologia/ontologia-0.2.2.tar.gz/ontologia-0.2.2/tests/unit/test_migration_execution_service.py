from __future__ import annotations

from sqlmodel import Session, select

from api.services.instances_service import InstancesService
from api.services.metamodel_service import MetamodelService
from api.services.migration_execution_service import MigrationExecutionService
from api.v2.schemas.instances import ObjectUpsertRequest
from api.v2.schemas.metamodel import ObjectTypePutRequest, PropertyDefinition
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.domain.metamodels.migrations.migration_task import (
    MigrationTask,
    MigrationTaskStatus,
)


def _create_object_type(session: Session, data_type: str) -> MigrationTask | None:
    metamodel = MetamodelService(session, service="ontology", instance="default")
    metamodel.upsert_object_type(
        "customer",
        ObjectTypePutRequest(
            displayName="Customer",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "age": PropertyDefinition(dataType=data_type, displayName="Age"),
            },
            implements=[],
        ),
    )
    return session.exec(select(MigrationTask)).first()


def test_migration_execution_service_applies_changes(session: Session) -> None:
    _create_object_type(session, "integer")

    instances = InstancesService(session, service="ontology", instance="default")
    instances.upsert_object(
        "customer",
        "1",
        ObjectUpsertRequest(properties={"age": 42}),
    )

    _create_object_type(session, "string")

    task = session.exec(select(MigrationTask)).first()
    assert task is not None

    executor = MigrationExecutionService(session)
    dry = executor.run_task("ontology", "default", task.rid, dry_run=True)
    assert dry["failedCount"] == 0

    result = executor.run_task("ontology", "default", task.rid)
    assert result["failedCount"] == 0
    assert result["updatedCount"] == 1

    session.refresh(task)
    assert task.status == MigrationTaskStatus.COMPLETED

    stored = session.exec(select(ObjectInstance).where(ObjectInstance.pk_value == "1")).first()
    assert stored is not None
    assert stored.data.get("age") == "42"


def test_migration_execution_service_handles_failure(session: Session) -> None:
    _create_object_type(session, "string")

    instances = InstancesService(session, service="ontology", instance="default")
    instances.upsert_object(
        "customer",
        "1",
        ObjectUpsertRequest(properties={"age": "not-a-number"}),
    )

    _create_object_type(session, "integer")

    task = session.exec(select(MigrationTask)).first()
    assert task is not None

    executor = MigrationExecutionService(session)
    result = executor.run_task("ontology", "default", task.rid)

    session.refresh(task)
    assert task.status == MigrationTaskStatus.FAILED
    assert result["failedCount"] == 1
    assert result["updatedCount"] == 0


def test_migration_execution_service_run_pending(session: Session) -> None:
    _create_object_type(session, "integer")

    instances = InstancesService(session, service="ontology", instance="default")
    instances.upsert_object(
        "customer",
        "1",
        ObjectUpsertRequest(properties={"age": 25}),
    )

    _create_object_type(session, "string")

    executor = MigrationExecutionService(session)
    dry_results = executor.run_pending_tasks("ontology", "default", dry_run=True)
    assert len(dry_results) == 1
    assert dry_results[0]["failedCount"] == 0

    applied_results = executor.run_pending_tasks("ontology", "default")
    assert len(applied_results) == 1
    assert applied_results[0]["failedCount"] == 0

    task = session.exec(select(MigrationTask)).first()
    assert task is not None
    assert task.status == MigrationTaskStatus.COMPLETED
