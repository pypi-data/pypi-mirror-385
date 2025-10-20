from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from api.services.metamodel_service import MetamodelService
from api.v2.schemas.metamodel import (
    LinkInverseDefinition,
    LinkTypePutRequest,
    ObjectTypePutRequest,
    PropertyDefinition,
)


def make_service() -> MetamodelService:
    svc = MetamodelService(session=MagicMock())
    # Substituir o repositório real por um mock
    svc.repo = MagicMock()
    return svc


def test_upsert_object_type_primary_key_missing_raises_400():
    service = make_service()

    schema = ObjectTypePutRequest(
        displayName="Customer",
        description=None,
        primaryKey="id",
        properties={
            # 'id' ausente
            "name": PropertyDefinition(dataType="string", displayName="Name")
        },
    )

    with pytest.raises(HTTPException) as exc:
        service.upsert_object_type("customer", schema)

    assert exc.value.status_code == 400
    assert "must be defined in properties" in exc.value.detail


def test_upsert_object_type_primary_key_not_required_raises_400():
    service = make_service()

    schema = ObjectTypePutRequest(
        displayName="Customer",
        description=None,
        primaryKey="id",
        properties={"id": PropertyDefinition(dataType="string", displayName="Id", required=False)},
    )

    with pytest.raises(HTTPException) as exc:
        service.upsert_object_type("customer", schema)

    assert exc.value.status_code == 400
    assert "must be required" in exc.value.detail


def test_upsert_link_type_from_object_type_missing_raises_400():
    service = make_service()
    # Primeiro get_object_type_by_api_name retorna None (from), segundo retorna algo (to)
    service.repo.get_object_type_by_api_name.side_effect = [None, MagicMock()]

    schema = LinkTypePutRequest(
        displayName="works_for",
        cardinality="MANY_TO_ONE",
        fromObjectType="employee",
        toObjectType="company",
        inverse=LinkInverseDefinition(apiName="has_employees", displayName="has employees"),
        description=None,
    )

    with pytest.raises(HTTPException) as exc:
        service.upsert_link_type("works_for", schema)

    assert exc.value.status_code == 400
    assert "not found" in exc.value.detail
