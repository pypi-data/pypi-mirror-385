"""
test_api.py
-----------
Testes para a API REST (Foundry-compatible).

Testa:
- Endpoints de ObjectType
- Endpoints de LinkType
- Validações
- Error handling
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from api.core.database import get_session
from api.main import app

# --- Fixtures ---


@pytest.fixture(name="session")
def session_fixture():
    """
    Cria uma sessão de DB em memória para testes.
    """
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Cria um TestClient do FastAPI com override da session.
    """

    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


# --- Health Check Tests ---


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Ontology Stack API"
    assert data["status"] == "running"


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data


# --- ObjectType Tests ---


def test_create_object_type(client: TestClient):
    """Test creating a new ObjectType."""
    payload = {
        "displayName": "Employee",
        "description": "An employee in the organization",
        "primaryKey": "employee_id",
        "properties": {
            "employee_id": {"dataType": "string", "displayName": "Employee ID", "required": True},
            "name": {"dataType": "string", "displayName": "Full Name", "required": True},
            "age": {"dataType": "integer", "displayName": "Age", "required": False},
        },
    }

    response = client.put("/v2/ontologies/default/objectTypes/employee", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["apiName"] == "employee"
    assert data["displayName"] == "Employee"
    assert data["primaryKey"] == "employee_id"
    assert "rid" in data
    assert len(data["properties"]) == 3


def test_get_object_type(client: TestClient):
    """Test getting an ObjectType."""
    # First create
    payload = {
        "displayName": "Customer",
        "primaryKey": "customer_id",
        "properties": {
            "customer_id": {"dataType": "string", "displayName": "Customer ID", "required": True}
        },
    }

    create_response = client.put("/v2/ontologies/default/objectTypes/customer", json=payload)
    assert create_response.status_code == 200

    # Then get
    response = client.get("/v2/ontologies/default/objectTypes/customer")

    assert response.status_code == 200
    data = response.json()
    assert data["apiName"] == "customer"


def test_list_object_types(client: TestClient):
    """Test listing all ObjectTypes."""
    # Create a few ObjectTypes
    for name in ["person", "company", "product"]:
        payload = {
            "displayName": name.capitalize(),
            "primaryKey": "id",
            "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
        }
        client.put(f"/v2/ontologies/default/objectTypes/{name}", json=payload)

    # List all
    response = client.get("/v2/ontologies/default/objectTypes")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) >= 3


def test_delete_object_type(client: TestClient):
    """Test deleting an ObjectType."""
    # Create
    payload = {
        "displayName": "ToDelete",
        "primaryKey": "id",
        "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
    }
    client.put("/v2/ontologies/default/objectTypes/to_delete", json=payload)

    # Delete
    response = client.delete("/v2/ontologies/default/objectTypes/to_delete")
    assert response.status_code == 204

    # Verify deletion
    response = client.get("/v2/ontologies/default/objectTypes/to_delete")
    assert response.status_code == 404


def test_object_type_validation_primary_key_missing(client: TestClient):
    """Test validation: primary key must be in properties."""
    payload = {
        "displayName": "Invalid",
        "primaryKey": "missing_key",
        "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
    }

    response = client.put("/v2/ontologies/default/objectTypes/invalid", json=payload)
    assert response.status_code == 400
    assert "must be defined in properties" in response.json()["detail"]


def test_object_type_validation_primary_key_not_required(client: TestClient):
    """Test validation: primary key must be required."""
    payload = {
        "displayName": "Invalid",
        "primaryKey": "id",
        "properties": {
            "id": {"dataType": "string", "displayName": "ID", "required": False}  # Should be True
        },
    }

    response = client.put("/v2/ontologies/default/objectTypes/invalid", json=payload)
    assert response.status_code == 400
    assert "must be required" in response.json()["detail"]


# --- LinkType Tests ---


def test_create_link_type(client: TestClient):
    """Test creating a new LinkType."""
    # First create ObjectTypes
    employee_payload = {
        "displayName": "Employee",
        "primaryKey": "id",
        "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
    }
    department_payload = {
        "displayName": "Department",
        "primaryKey": "id",
        "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
    }

    client.put("/v2/ontologies/default/objectTypes/employee", json=employee_payload)
    client.put("/v2/ontologies/default/objectTypes/department", json=department_payload)

    # Create LinkType
    link_payload = {
        "displayName": "Works In",
        "cardinality": "MANY_TO_ONE",
        "fromObjectType": "employee",
        "toObjectType": "department",
        "inverse": {"apiName": "employees", "displayName": "Employees"},
    }

    response = client.put("/v2/ontologies/default/linkTypes/worksIn", json=link_payload)

    assert response.status_code == 200
    data = response.json()

    assert data["apiName"] == "worksIn"
    assert data["displayName"] == "Works In"
    assert data["cardinality"] == "MANY_TO_ONE"
    assert data["fromObjectType"] == "employee"
    assert data["toObjectType"] == "department"
    assert data["inverse"]["apiName"] == "employees"


def test_get_link_type(client: TestClient):
    """Test getting a LinkType."""
    # Setup ObjectTypes
    for name in ["user", "group"]:
        payload = {
            "displayName": name.capitalize(),
            "primaryKey": "id",
            "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
        }
        client.put(f"/v2/ontologies/default/objectTypes/{name}", json=payload)

    # Create LinkType
    link_payload = {
        "displayName": "Member Of",
        "cardinality": "MANY_TO_MANY",
        "fromObjectType": "user",
        "toObjectType": "group",
        "inverse": {"apiName": "members", "displayName": "Members"},
    }
    client.put("/v2/ontologies/default/linkTypes/memberOf", json=link_payload)

    # Get LinkType
    response = client.get("/v2/ontologies/default/linkTypes/memberOf")

    assert response.status_code == 200
    data = response.json()
    assert data["apiName"] == "memberOf"


def test_list_link_types(client: TestClient):
    """Test listing all LinkTypes."""
    # Setup ObjectTypes
    for name in ["a", "b"]:
        payload = {
            "displayName": name.upper(),
            "primaryKey": "id",
            "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
        }
        client.put(f"/v2/ontologies/default/objectTypes/{name}", json=payload)

    # Create LinkTypes
    for i, cardinality in enumerate(["ONE_TO_ONE", "ONE_TO_MANY"]):
        link_payload = {
            "displayName": f"Link {i}",
            "cardinality": cardinality,
            "fromObjectType": "a",
            "toObjectType": "b",
            "inverse": {"apiName": f"inverse{i}", "displayName": f"Inverse {i}"},
        }
        client.put(f"/v2/ontologies/default/linkTypes/link{i}", json=link_payload)

    # List
    response = client.get("/v2/ontologies/default/linkTypes")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) >= 2


def test_delete_link_type(client: TestClient):
    """Test deleting a LinkType."""
    # Setup
    for name in ["x", "y"]:
        payload = {
            "displayName": name.upper(),
            "primaryKey": "id",
            "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
        }
        client.put(f"/v2/ontologies/default/objectTypes/{name}", json=payload)

    link_payload = {
        "displayName": "To Delete",
        "cardinality": "ONE_TO_ONE",
        "fromObjectType": "x",
        "toObjectType": "y",
        "inverse": {"apiName": "inverseDelete", "displayName": "Inverse Delete"},
    }
    client.put("/v2/ontologies/default/linkTypes/toDelete", json=link_payload)

    # Delete
    response = client.delete("/v2/ontologies/default/linkTypes/toDelete")
    assert response.status_code == 204

    # Verify
    response = client.get("/v2/ontologies/default/linkTypes/toDelete")
    assert response.status_code == 404


def test_link_type_validation_object_type_not_found(client: TestClient):
    """Test validation: ObjectTypes must exist."""
    link_payload = {
        "displayName": "Invalid Link",
        "cardinality": "ONE_TO_ONE",
        "fromObjectType": "nonexistent",
        "toObjectType": "alsoNonexistent",
        "inverse": {"apiName": "inverse", "displayName": "Inverse"},
    }

    response = client.put("/v2/ontologies/default/linkTypes/invalid", json=link_payload)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
