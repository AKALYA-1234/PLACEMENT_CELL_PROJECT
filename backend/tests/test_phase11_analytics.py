import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db, Base, engine
from app.models.admin_user import AdminUser
from app.utils.security import create_access_token, hash_password

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_header():
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
    return {"Authorization": f"Bearer {token}"}


def test_analytics_overview(auth_header):
    response = client.get("/admin/analytics/overview", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert "total_companies" in data
    assert "total_registrations" in data
    assert "students_placed" in data
    assert "students_in_process" in data
    assert "students_not_placed" in data
    assert "total_placement_records" in data


def test_analytics_departments(auth_header):
    response = client.get("/admin/analytics/departments", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "departments" in data
    assert "total_departments" in data


def test_analytics_companies(auth_header):
    response = client.get("/admin/analytics/companies", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert "total_companies" in data


def test_analytics_rounds(auth_header):
    response = client.get("/admin/analytics/rounds", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "rounds" in data


def test_analytics_student_not_found(auth_header):
    response = client.get("/admin/analytics/student/NONEXISTENT999", headers=auth_header)
    assert response.status_code == 404
