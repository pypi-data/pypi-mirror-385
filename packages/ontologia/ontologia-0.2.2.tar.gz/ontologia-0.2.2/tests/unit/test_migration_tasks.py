from sqlmodel import Session, select

from api.services.metamodel_service import MetamodelService
from api.v2.schemas.metamodel import ObjectTypePutRequest, PropertyDefinition
from ontologia.domain.metamodels.migrations.migration_task import MigrationTask, MigrationTaskStatus


def test_migration_task_created_on_destructive_change(session: Session) -> None:
    svc = MetamodelService(session, service="ontology", instance="default")

    svc.upsert_object_type(
        "entity",
        ObjectTypePutRequest(
            displayName="Entity",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "age": PropertyDefinition(dataType="integer", displayName="Age"),
            },
            implements=[],
        ),
    )

    svc.upsert_object_type(
        "entity",
        ObjectTypePutRequest(
            displayName="Entity",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "age": PropertyDefinition(dataType="string", displayName="Age"),
            },
            implements=[],
        ),
    )

    task = session.exec(select(MigrationTask)).first()
    assert task is not None
    assert task.object_type_api_name == "entity"
    assert task.status == MigrationTaskStatus.PENDING
    assert task.from_version == 1
    assert task.to_version == 2
    operations = task.plan.get("operations", [])
    assert any(op.get("operation") == "change_type" for op in operations)
