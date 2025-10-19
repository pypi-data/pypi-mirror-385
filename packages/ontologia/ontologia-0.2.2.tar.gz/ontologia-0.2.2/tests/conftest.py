import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Ensure project root is on PYTHONPATH so 'api' package is importable
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from api.core.auth import UserPrincipal, get_current_user
from api.core.database import get_session
from api.main import app


@pytest.fixture(name="session")
def session_fixture():
    # In-memory SQLite shared across threads via StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        yield session

    test_principal = UserPrincipal(user_id="test", roles=["admin"], tenants={})

    async def get_current_user_override():
        return test_principal

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
