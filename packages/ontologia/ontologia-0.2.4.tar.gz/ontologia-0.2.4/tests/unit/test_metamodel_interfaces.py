from sqlmodel import Session

from api.services.metamodel_service import MetamodelService
from api.v2.schemas.metamodel import (
    InterfacePutRequest,
    ObjectTypePutRequest,
    PropertyDefinition,
)


def test_interfaces_crud_and_implements(session: Session):
    svc = MetamodelService(session, service="ontology", instance="default")

    # Create Interface
    iresp = svc.upsert_interface_type(
        "Localizavel",
        InterfacePutRequest(
            displayName="Localizável",
            description="Qualquer coisa com endereço.",
            properties={"address": {"dataType": "string", "displayName": "Address"}},
        ),
    )
    assert iresp.apiName == "Localizavel"
    assert iresp.version == 1
    assert iresp.isLatest is True

    # Create ObjectType that implements the Interface
    oresp = svc.upsert_object_type(
        "cliente",
        ObjectTypePutRequest(
            displayName="Cliente",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "name": PropertyDefinition(dataType="string", displayName="Name"),
                "address": PropertyDefinition(dataType="string", displayName="Address"),
            },
            implements=["Localizavel"],
        ),
    )
    assert oresp.apiName == "cliente"
    assert "Localizavel" in oresp.implements
    assert oresp.version == 1
    assert oresp.isLatest is True

    # Update: remove implements
    oresp2 = svc.upsert_object_type(
        "cliente",
        ObjectTypePutRequest(
            displayName="Cliente",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "name": PropertyDefinition(dataType="string", displayName="Name"),
                "address": PropertyDefinition(dataType="string", displayName="Address"),
            },
            implements=[],
        ),
    )
    assert oresp2.implements == []
    assert oresp2.version == 2
    assert oresp2.isLatest is True

    # Delete Interface
    assert svc.delete_interface_type("Localizavel") is True
