from fastapi.testclient import TestClient

from app.main import app


def test_root_route_is_available() -> None:
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200


def test_auth_routes_are_versioned() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "doesnotexist@example.com", "password": "wrong", "portal": "employee"},
        )
    assert response.status_code == 401
