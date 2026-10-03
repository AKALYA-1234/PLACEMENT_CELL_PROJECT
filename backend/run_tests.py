import sys
import os
import traceback
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import get_db, Base, engine
from app.models.admin_user import AdminUser
from app.utils.security import create_access_token, hash_password

from tests.test_excel_parser import (
    test_register_number_normalizer,
    test_status_normalizer,
    test_parse_netgear_workbook,
    test_parse_presidio_workbook,
    test_parse_soliton_workbook
)
from tests.test_db_ingestion import (
    test_db_ingestion_presidio,
    test_db_ingestion_soliton
)
from tests.test_import_validation import (
    test_validate_import_service_netgear,
    test_validate_import_endpoint_presidio,
    test_validate_import_endpoint_soliton
)
from tests.test_import_confirm import (
    test_confirm_import_presidio_endpoint,
    test_confirm_import_idempotency,
    test_confirm_import_unvalidated_rejection
)
from tests.test_auth import (
    test_login_success,
    test_login_invalid_password,
    test_login_invalid_email,
    test_get_me_success,
    test_get_me_unauthorized,
    test_logout_endpoint,
    test_protected_import_validate_unauthorized,
    test_protected_import_confirm_unauthorized,
    test_protected_import_validate_with_token
)
from tests.test_admin_apis import (
    test_imports_api,
    test_students_api,
    test_companies_api,
    test_analytics_api
)
from tests.test_phase11_analytics import (
    test_analytics_overview,
    test_analytics_departments,
    test_analytics_companies,
    test_analytics_rounds,
    test_analytics_student_not_found
)

def run():
    print("=== RUNNING PHASE 4 - 11 FULL TEST SUITE ===")

    # Ensure admin user for auth headers
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
    auth_hdr = {"Authorization": f"Bearer {token}"}

    tests = [
        ("Register Normalizer", test_register_number_normalizer),
        ("Status Normalizer", test_status_normalizer),
        ("Netgear Workbook Parser", test_parse_netgear_workbook),
        ("Presidio Workbook Parser", test_parse_presidio_workbook),
        ("Soliton Workbook Parser", test_parse_soliton_workbook),
        ("Presidio DB Ingestion Bridge", test_db_ingestion_presidio),
        ("Soliton DB Ingestion Bridge", test_db_ingestion_soliton),
        ("Netgear Import Validation Service", test_validate_import_service_netgear),
        ("Presidio Import Validation API (POST /admin/import/validate)", test_validate_import_endpoint_presidio),
        ("Soliton Import Validation API (POST /admin/import/validate)", test_validate_import_endpoint_soliton),
        ("Presidio Import Confirm API (POST /admin/import/confirm)", test_confirm_import_presidio_endpoint),
        ("Import Confirm Idempotency Test", test_confirm_import_idempotency),
        ("Unvalidated Import Rejection Test", test_confirm_import_unvalidated_rejection),
        ("Admin Login Success", test_login_success),
        ("Admin Login Invalid Password Rejection", test_login_invalid_password),
        ("Admin Login Invalid Email Rejection", test_login_invalid_email),
        ("Admin /me Endpoint Success", test_get_me_success),
        ("Admin /me Endpoint Unauthorized Rejection", test_get_me_unauthorized),
        ("Admin Logout Endpoint", test_logout_endpoint),
        ("Protected Import Validate Endpoint 401 Check", test_protected_import_validate_unauthorized),
        ("Protected Import Confirm Endpoint 401 Check", test_protected_import_confirm_unauthorized),
        ("Protected Import Validate Endpoint Token Authorized", test_protected_import_validate_with_token),
        ("Admin Imports List & Detail API", test_imports_api),
        ("Admin Students List & Detail API", test_students_api),
        ("Admin Companies, Drives & Stats API", test_companies_api),
        ("Admin Analytics Overview, Depts, Companies & Rounds API", test_analytics_api),
        ("Phase 11: Analytics Overview Metrics", test_analytics_overview),
        ("Phase 11: Analytics Departments Breakdown", test_analytics_departments),
        ("Phase 11: Analytics Companies Breakdown", test_analytics_companies),
        ("Phase 11: Analytics Round Funnel", test_analytics_rounds),
        ("Phase 11: Analytics Student Not Found", test_analytics_student_not_found),
    ]

    passed = 0
    failed = 0
    for name, func in tests:
        print(f"\n--- Running: {name} ---")
        try:
            if "auth_header" in func.__code__.co_varnames:
                func(auth_header=auth_hdr)
            else:
                func()
            print(f"--> [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"--> [FAIL] {name}: {type(e).__name__}: {e}")
            traceback.print_exc(file=sys.stdout)
            failed += 1

    print(f"\n==========================================")
    print(f"Test Summary: {passed} passed, {failed} failed out of {len(tests)} tests.")
    print(f"==========================================")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run()
