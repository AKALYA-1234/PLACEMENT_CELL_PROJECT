import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

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

def run():
    print("=== RUNNING PHASE 4, 5, 6, & 7 FULL TEST SUITE ===")
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
    ]
    
    passed = 0
    failed = 0
    for name, func in tests:
        print(f"\n--- Running: {name} ---")
        try:
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
