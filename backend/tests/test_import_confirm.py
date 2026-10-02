import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from app.main import app
from app.database import SessionLocal
from app.models import Company, PlacementDrive, PlacementStage, StudentRegistration, StudentStageResult, Placement, ImportLog

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data"))
client = TestClient(app)


def get_auth_headers():
    login_res = client.post(
        "/api/auth/login",
        json={"email": "admin@college.edu", "password": "admin123"}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_confirm_import_presidio_endpoint():
    file_path = os.path.join(SAMPLE_DIR, "PRESIDIO.xlsx")
    assert os.path.exists(file_path)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/admin/import/confirm",
        data={
            "company_name": "Presidio Final Drive",
            "academic_year": "2025-2026"
        },
        files={
            "file": ("PRESIDIO.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "SUCCESS"
    assert data["company_name"] == "Presidio Final Drive"

    db = SessionLocal()
    try:
        company = db.scalar(select(Company).where(Company.name == "Presidio Final Drive"))
        assert company is not None

        drive = db.scalar(select(PlacementDrive).where(PlacementDrive.company_id == company.id))
        assert drive is not None

        placements = db.scalars(select(Placement).where(Placement.drive_id == drive.id)).all()
        assert len(placements) == 3

        for p in placements:
            assert p.status == "PLACED"
            assert p.status != "ACCEPTED"

    finally:
        db.close()


def test_confirm_import_idempotency():
    file_path = os.path.join(SAMPLE_DIR, "Soliton Roundwise Details.xlsx")
    assert os.path.exists(file_path)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    headers = get_auth_headers()

    res1 = client.post(
        "/admin/import/confirm",
        data={
            "company_name": "Soliton Idempotent Inc",
            "academic_year": "2025-2026"
        },
        files={
            "file": ("Soliton Roundwise Details.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        },
        headers=headers
    )
    assert res1.status_code == 200

    res2 = client.post(
        "/admin/import/confirm",
        data={
            "company_name": "Soliton Idempotent Inc",
            "academic_year": "2025-2026"
        },
        files={
            "file": ("Soliton Roundwise Details.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        },
        headers=headers
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "SUCCESS"


def test_confirm_import_unvalidated_rejection():
    file_path = os.path.join(SAMPLE_DIR, "Netgear - Roundwise.xlsx")
    assert os.path.exists(file_path)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/admin/import/confirm",
        data={
            "company_name": "Netgear Unvalidated Drive",
            "academic_year": "2025-2026"
        },
        files={
            "file": ("Netgear - Roundwise.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        },
        headers=get_auth_headers()
    )

    assert response.status_code == 400
    data = response.json()
    assert "Cannot confirm import" in data["detail"] or "malformed" in data["detail"]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
