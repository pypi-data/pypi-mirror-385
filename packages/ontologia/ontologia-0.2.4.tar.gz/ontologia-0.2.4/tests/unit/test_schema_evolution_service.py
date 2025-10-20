from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from sqlmodel import Session, select

from api.services.metamodel_service import MetamodelService
from api.services.schema_evolution_service import SchemaEvolutionService
from api.v2.schemas.metamodel import ObjectTypePutRequest, PropertyDefinition
from ontologia.domain.metamodels.migrations.migration_task import (
    MigrationTask,
    MigrationTaskStatus,
)


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle)


def test_plan_and_apply_schema_changes(session: Session, tmp_path: Path) -> None:
    metamodel = MetamodelService(session, service="ontology", instance="default")
    definitions_dir = tmp_path / "defs"

    _write_yaml(
        definitions_dir / "object_types" / "customer.yml",
        {
            "apiName": "customer",
            "displayName": "Customer",
            "description": "",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
            "implements": [],
        },
    )

    service = SchemaEvolutionService(
        metamodel,
        definitions_dir=definitions_dir,
    )

    plan = service.plan_schema_changes()
    assert plan["plan"]
    assert plan["plan"][0]["action"] == "create"

    apply_result = service.apply_schema_changes(allow_destructive=True)
    assert apply_result["applied"]
    created = metamodel.get_object_type("customer")
    assert created is not None
    assert created.displayName == "Customer"


def test_apply_schema_changes_requires_destructive_flag(session: Session, tmp_path: Path) -> None:
    metamodel = MetamodelService(session, service="ontology", instance="default")

    metamodel.upsert_object_type(
        "entity",
        ObjectTypePutRequest(
            displayName="Entity",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "value": PropertyDefinition(dataType="string", displayName="Value"),
            },
            implements=[],
        ),
    )

    definitions_dir = tmp_path / "defs"
    _write_yaml(
        definitions_dir / "object_types" / "entity.yml",
        {
            "apiName": "entity",
            "displayName": "Entity",
            "description": "",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
            },
            "implements": [],
        },
    )

    service = SchemaEvolutionService(
        metamodel,
        definitions_dir=definitions_dir,
    )

    plan = service.plan_schema_changes()
    assert plan["plan"] and plan["plan"][0]["dangerous"] is True

    with pytest.raises(ValueError):
        service.apply_schema_changes(allow_destructive=False)


def test_schema_migration_task_lifecycle(session: Session, tmp_path: Path) -> None:
    metamodel = MetamodelService(session, service="ontology", instance="default")

    metamodel.upsert_object_type(
        "thing",
        ObjectTypePutRequest(
            displayName="Thing",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "age": PropertyDefinition(dataType="integer", displayName="Age"),
            },
            implements=[],
        ),
    )

    metamodel.upsert_object_type(
        "thing",
        ObjectTypePutRequest(
            displayName="Thing",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "age": PropertyDefinition(dataType="string", displayName="Age"),
            },
            implements=[],
        ),
    )

    service = SchemaEvolutionService(metamodel, definitions_dir=tmp_path / "defs")

    tasks = service.list_migration_tasks()
    assert tasks
    assert tasks[0]["status"] == MigrationTaskStatus.PENDING.value

    rid = tasks[0]["rid"]
    updated = service.update_migration_task(rid, status="COMPLETED")
    assert updated["status"] == MigrationTaskStatus.COMPLETED.value

    stored = session.exec(select(MigrationTask).where(MigrationTask.rid == rid)).first()
    assert stored is not None
    assert stored.status == MigrationTaskStatus.COMPLETED
