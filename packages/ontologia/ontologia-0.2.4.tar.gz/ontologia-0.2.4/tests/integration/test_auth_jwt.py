from fastapi.testclient import TestClient

from api.core.database import get_session
from api.main import app


def _override_session(session):
    def _override():
        yield session

    app.dependency_overrides[get_session] = _override


def _clear_overrides():
    app.dependency_overrides.clear()


def test_obtain_token_and_access_protected_route(session):
    _override_session(session)
    try:
        with TestClient(app) as client:
            token_resp = client.post(
                "/v2/auth/token",
                data={"username": "admin", "password": "admin"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            assert token_resp.status_code == 200, token_resp.text
            token = token_resp.json()["access_token"]

            resp = client.get(
                "/v2/ontologies/default/objectTypes",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200, resp.text
    finally:
        _clear_overrides()


def test_forbidden_when_role_insufficient(session):
    _override_session(session)
    try:
        with TestClient(app) as client:
            token_resp = client.post(
                "/v2/auth/token",
                data={"username": "viewer", "password": "viewer"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            assert token_resp.status_code == 200, token_resp.text
            token = token_resp.json()["access_token"]

            resp = client.delete(
                "/v2/ontologies/default/objectTypes/example",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 403
    finally:
        _clear_overrides()


def test_missing_token_returns_unauthorized(session):
    _override_session(session)
    try:
        with TestClient(app) as client:
            resp = client.get("/v2/ontologies/default/objectTypes")
            assert resp.status_code == 401
    finally:
        _clear_overrides()
