import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db, Base, engine
from app.models.admin_user import AdminUser
from app.utils.security import create_access_token, hash_password
from app.api.import_routes import sanitize_filename

client = TestClient(app)


def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd.xlsx") == "passwd.xlsx"
    assert sanitize_filename("my_file<script>.xlsx") == "my_file_script_.xlsx"
    assert sanitize_filename("Normal_Workbook_2025.xlsx") == "Normal_Workbook_2025.xlsx"


def test_file_size_limit_exceeded():
    Base.metadata.create_all(bind=engine)
    db: Session = next(get_db())
    admin = db.query(AdminUser).filter_by(email="admin@college.edu").first()
    if not admin:
        admin = AdminUser(
            email="admin@college.edu",
            hashed_password=hash_password("admin123"),
            full_name="Placement Director",
            role="SUPER_ADMIN",
            is_active=True
        )
        db.add(admin)
        db.commit()

    token = create_access_token(data={"sub": admin.email})

    # Create dummy payload larger than 15 MB
    large_payload = b"X" * (16 * 1024 * 1024)

    response = client.post(
        "/admin/import/validate",
        data={"company_name": "Large File Co", "academic_year": "2025-2026"},
        files={"file": ("large_file.xlsx", large_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 413
    assert "exceeds maximum allowed size limit" in response.json()["detail"]


def test_cors_preflight():
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_invalid_jwt_token_rejection():
    response = client.get(
        "/admin/analytics/overview",
        headers={"Authorization": "Bearer fake.invalid.jwt.token"}
    )
    assert response.status_code == 401
