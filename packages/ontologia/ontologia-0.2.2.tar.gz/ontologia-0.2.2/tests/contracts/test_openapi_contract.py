from __future__ import annotations

import schemathesis
from fastapi.testclient import TestClient

from api.core.database import get_session
from api.main import app

schema = schemathesis.openapi.from_asgi("/openapi.json", app)


def _seed_baseline() -> None:
    client = TestClient(app)
    client.put(
        "/v2/ontologies/default/objectTypes/employee",
        json={
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
            },
        },
    )


def test_openapi_spec_is_valid():
    schema.validate()


def test_openapi_contract_object_types(session):
    def override():
        yield session

    app.dependency_overrides[get_session] = override
    try:
        _seed_baseline()
        client = TestClient(app)
        response = client.get("/v2/ontologies/default/objectTypes")
        operation = schema["/v2/ontologies/{ontologyApiName}/objectTypes"]["get"]
        st_response = schemathesis.Response.from_any(response)
        schema.validate_response(operation, st_response)
    finally:
        app.dependency_overrides.clear()


def test_openapi_contract_objects(session):
    def override():
        yield session

    app.dependency_overrides[get_session] = override
    try:
        client = TestClient(app)
        client.put(
            "/v2/ontologies/default/objectTypes/employee",
            json={
                "displayName": "Employee",
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                },
            },
        )
        client.put(
            "/v2/ontologies/default/objects/employee/e1",
            json={"properties": {"id": "e1"}},
        )
        response = client.get(
            "/v2/ontologies/default/objects",
            params={"objectType": "employee"},
        )
        operation = schema["/v2/ontologies/{ontologyApiName}/objects"]["get"]
        st_response = schemathesis.Response.from_any(response)
        schema.validate_response(operation, st_response)
    finally:
        app.dependency_overrides.clear()
