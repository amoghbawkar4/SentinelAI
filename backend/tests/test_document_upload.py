from fastapi.testclient import TestClient

from app.core.demo_users import DEMO_USERS
from app.database.init_db import seed_default_roles
from app.main import app
from app.services.redis_service import RedisService


def test_document_upload_persists_metadata_for_authorized_role() -> None:
    seed_default_roles()
    RedisService().delete_value("ratelimit:/api/v1/auth/login:testclient")

    with TestClient(app) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "hr@company.com", "password": "hr123", "login_as": "HR", "portal": "employee"},
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("Compensation_Policy.pdf", b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF", "application/pdf")},
            data={"allowed_roles": ["HR", "Payroll Administrator"]},
        )

        assert response.status_code == 201, response.text
        payload = response.json()
        assert payload["original_filename"] == "Compensation_Policy.pdf"
        assert payload["processing_status"] == "RECEIVED"
        assert payload["allowed_roles"] == ["HR", "Payroll Administrator"]


def test_document_upload_rejects_non_uploader_roles() -> None:
    seed_default_roles()
    RedisService().delete_value("ratelimit:/api/v1/auth/login:testclient")

    with TestClient(app) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "employee@company.com", "password": "employee123", "login_as": "Employee", "portal": "employee"},
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("Employee_Salary.pdf", b"fake pdf", "application/pdf")},
            data={"allowed_roles": ["Employee"]},
        )

        assert response.status_code == 403
