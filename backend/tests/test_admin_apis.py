import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_auth_headers():
    login_res = client.post(
        "/api/auth/login",
        json={"email": "admin@college.edu", "password": "admin123"}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_imports_api():
    headers = get_auth_headers()

    # List Imports
    res = client.get("/admin/imports", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total"] >= 0

    if data["items"]:
        import_id = data["items"][0]["id"]
        detail_res = client.get(f"/admin/imports/{import_id}", headers=headers)
        assert detail_res.status_code == 200
        assert detail_res.json()["id"] == import_id


def test_students_api():
    headers = get_auth_headers()

    # List Students
    res = client.get("/admin/students?page=1&limit=10&sort_by=cgpa&order=desc", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0

    reg_no = data["items"][0]["register_number"]

    # Student Detail
    detail_res = client.get(f"/admin/students/{reg_no}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["register_number"] == reg_no
    assert "drives_history" in detail_data


def test_companies_api():
    headers = get_auth_headers()

    # List Companies
    res = client.get("/admin/companies", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0

    company_id = data["items"][0]["id"]

    # Company Detail
    detail_res = client.get(f"/admin/companies/{company_id}", headers=headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == company_id

    # Company Students
    students_res = client.get(f"/admin/companies/{company_id}/students", headers=headers)
    assert students_res.status_code == 200

    # Company Statistics
    stats_res = client.get(f"/admin/companies/{company_id}/statistics", headers=headers)
    assert stats_res.status_code == 200
    assert "selection_rate_percentage" in stats_res.json()


def test_analytics_api():
    headers = get_auth_headers()

    # Analytics Overview
    overview_res = client.get("/admin/analytics/overview", headers=headers)
    assert overview_res.status_code == 200
    overview_data = overview_res.json()
    assert "total_students" in overview_data
    assert "placement_rate_percentage" in overview_data

    # Analytics Departments
    dept_res = client.get("/admin/analytics/departments", headers=headers)
    assert dept_res.status_code == 200
    assert "departments" in dept_res.json()

    # Analytics Companies
    comp_res = client.get("/admin/analytics/companies", headers=headers)
    assert comp_res.status_code == 200
    assert "companies" in comp_res.json()

    # Analytics Rounds
    rounds_res = client.get("/admin/analytics/rounds", headers=headers)
    assert rounds_res.status_code == 200
    assert "rounds" in rounds_res.json()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
