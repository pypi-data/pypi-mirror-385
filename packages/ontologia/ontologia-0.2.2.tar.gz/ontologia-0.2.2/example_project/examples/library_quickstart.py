"""
examples/library_quickstart.py
------------------------------
Minimal end-to-end example using the library (services) directly without HTTP.
"""

from __future__ import annotations

import os
import sys

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from api.services.instances_service import InstancesService
from api.services.linked_objects_service import LinkedObjectsService
from api.services.metamodel_service import MetamodelService
from api.v2.schemas.instances import ObjectUpsertRequest
from api.v2.schemas.linked_objects import LinkCreateRequest
from api.v2.schemas.metamodel import LinkTypePutRequest, ObjectTypePutRequest


def main() -> bool:
    # In-memory DB shared across sessions
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Initialize services (service/instance align with API defaults)
        meta = MetamodelService(session, service="ontology", instance="default")
        inst = InstancesService(session, service="ontology", instance="default")
        links = LinkedObjectsService(session, service="ontology", instance="default")

        # 1) Upsert ObjectTypes
        meta.upsert_object_type(
            "employee",
            ObjectTypePutRequest(
                displayName="Employee",
                primaryKey="id",
                properties={"id": {"dataType": "string", "displayName": "ID", "required": True}},
            ),
        )
        meta.upsert_object_type(
            "company",
            ObjectTypePutRequest(
                displayName="Company",
                primaryKey="id",
                properties={"id": {"dataType": "string", "displayName": "ID", "required": True}},
            ),
        )

        # 2) Upsert LinkType (employee -> company)
        meta.upsert_link_type(
            "works_for",
            LinkTypePutRequest(
                displayName="Works For",
                cardinality="MANY_TO_ONE",
                fromObjectType="employee",
                toObjectType="company",
                inverse={"apiName": "has_employees", "displayName": "Has Employees"},
            ),
        )

        # 3) Upsert instances
        inst.upsert_object("employee", "e1", body=ObjectUpsertRequest(properties={}))
        inst.upsert_object("company", "c1", body=ObjectUpsertRequest(properties={}))

        # 4) Create link
        links.create_link("works_for", LinkCreateRequest(fromPk="e1", toPk="c1"))

        # 5) Traverse from employee to company
        traversal = inst.get_linked_objects("employee", "e1", "works_for", limit=10, offset=0)
        print("Traversal result:", traversal.model_dump())

    return True


if __name__ == "__main__":
    ok = main()
    print("OK" if ok else "FAIL")
