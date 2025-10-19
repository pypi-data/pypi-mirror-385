from fastapi.testclient import TestClient
from sqlmodel import SQLModel, select

from api.repositories.instances_repository import InstancesRepository
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.domain.metamodels.types.object_type import ObjectType


def _create_employee_object_type(client: TestClient):
    resp = client.put(
        "/v2/ontologies/default/objectTypes/employee",
        json={
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
        },
    )
    assert resp.status_code == 200


def test_instances_repository_crud_flow(client: TestClient, session):
    # Ensure metadata includes newly added instance tables
    SQLModel.metadata.create_all(session.get_bind())

    _create_employee_object_type(client)

    # Resolve ObjectType
    ot = session.exec(select(ObjectType).where(ObjectType.api_name == "employee")).one()

    repo = InstancesRepository(session)

    # Create and save instance
    inst = ObjectInstance(
        service="ontology",
        instance="default",
        api_name="employee_1",
        display_name="Employee 1",
        object_type_api_name="employee",
        object_type_rid=ot.rid,
        pk_value="1",
        data={"id": "1", "name": "Alice"},
    )
    saved = repo.save_object_instance(inst)
    assert saved.rid is not None

    # Get
    got = repo.get_object_instance("ontology", "default", "employee", "1")
    assert got is not None
    assert got.data["name"] == "Alice"

    # List
    lst = repo.list_object_instances("ontology", "default", object_type_api_name="employee")
    assert len(lst) == 1

    # Update
    got.data["name"] = "Alice Smith"
    repo.save_object_instance(got)
    got2 = repo.get_object_instance("ontology", "default", "employee", "1")
    assert got2.data["name"] == "Alice Smith"

    # Delete
    ok = repo.delete_object_instance("ontology", "default", "employee", "1")
    assert ok is True
    none = repo.get_object_instance("ontology", "default", "employee", "1")
    assert none is None

    # Delete again -> False
    ok2 = repo.delete_object_instance("ontology", "default", "employee", "1")
    assert ok2 is False
