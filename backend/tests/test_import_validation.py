import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.services.excel_parser.import_validation_service import validate_excel_import
from app.services.excel_parser.validation_models import ImportValidationResponse

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data"))
client = TestClient(app)


def get_auth_headers():
    login_res = client.post(
        "/api/auth/login",
        json={"email": "admin@college.edu", "password": "admin123"}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_validate_import_service_netgear():
    file_path = os.path.join(SAMPLE_DIR, "Netgear - Roundwise.xlsx")
    assert os.path.exists(file_path)

    db = SessionLocal()
    try:
        response: ImportValidationResponse = validate_excel_import(
            file_input=file_path,
            file_name="Netgear - Roundwise.xlsx",
            company_name="Netgear Inc",
            academic_year="2025-2026",
            db=db
        )

        assert response.company_name == "Netgear Inc"
        assert response.total_sheets == 4
        assert response.registered_count == 333
        assert len(response.invalid_register_numbers) == 2
        assert response.is_valid_for_import is False

    finally:
        db.close()


def test_validate_import_endpoint_presidio():
    file_path = os.path.join(SAMPLE_DIR, "PRESIDIO.xlsx")
    assert os.path.exists(file_path)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/admin/import/validate",
        data={
            "company_name": "Presidio Systems",
            "academic_year": "2025-2026"
        },
        files={
            "file": ("PRESIDIO.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()

    assert data["company_name"] == "Presidio Systems"
    assert data["file_name"] == "PRESIDIO.xlsx"
    assert data["total_sheets"] == 3
    assert data["placed_count"] == 3
    assert data["is_valid_for_import"] is True


def test_validate_import_endpoint_soliton():
    file_path = os.path.join(SAMPLE_DIR, "Soliton Roundwise Details.xlsx")
    assert os.path.exists(file_path)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/admin/import/validate",
        data={
            "company_name": "Soliton Technologies",
            "academic_year": "2025-2026"
        },
        files={
            "file": ("Soliton Roundwise Details.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()

    assert data["company_name"] == "Soliton Technologies"
    assert data["placed_count"] == 7


if __name__ == "__main__":
    pytest.main(["-v", __file__])
