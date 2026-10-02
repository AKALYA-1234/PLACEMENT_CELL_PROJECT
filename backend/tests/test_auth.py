import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient

from app.main import app

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data"))
client = TestClient(app)


def test_login_success():
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@college.edu", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password():
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@college.edu", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_invalid_email():
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@college.edu", "password": "admin123"}
    )
    assert response.status_code == 401


def test_get_me_success():
    login_res = client.post(
        "/api/auth/login",
        json={"email": "admin@college.edu", "password": "admin123"}
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@college.edu"
    assert data["full_name"] == "Placement Director"
    assert data["is_active"] is True


def test_get_me_unauthorized():
    response = client.get("/api/auth/me")
    assert response.status_code == 401

    response_bad_token = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    assert response_bad_token.status_code == 401


def test_logout_endpoint():
    login_res = client.post(
        "/api/auth/login",
        json={"email": "admin@college.edu", "password": "admin123"}
    )
    token = login_res.json()["access_token"]

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "logged out" in response.json()["message"].lower()


def test_protected_import_validate_unauthorized():
    file_path = os.path.join(SAMPLE_DIR, "PRESIDIO.xlsx")
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # Attempt validate without Auth Header
    response = client.post(
        "/admin/import/validate",
        data={"company_name": "Presidio", "academic_year": "2025-2026"},
        files={"file": ("PRESIDIO.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 401


def test_protected_import_confirm_unauthorized():
    file_path = os.path.join(SAMPLE_DIR, "PRESIDIO.xlsx")
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # Attempt confirm without Auth Header
    response = client.post(
        "/admin/import/confirm",
        data={"company_name": "Presidio", "academic_year": "2025-2026"},
        files={"file": ("PRESIDIO.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 401


def test_protected_import_validate_with_token():
    login_res = client.post(
        "/api/auth/login",
        json={"email": "admin@college.edu", "password": "admin123"}
    )
    token = login_res.json()["access_token"]

    file_path = os.path.join(SAMPLE_DIR, "PRESIDIO.xlsx")
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/admin/import/validate",
        data={"company_name": "Presidio Protected", "academic_year": "2025-2026"},
        files={"file": ("PRESIDIO.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["company_name"] == "Presidio Protected"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
