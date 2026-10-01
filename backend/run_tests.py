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

def run():
    print("=== RUNNING PHASE 4 EXCEL PARSER UNIT TESTS ===")
    tests = [
        ("Register Normalizer", test_register_number_normalizer),
        ("Status Normalizer", test_status_normalizer),
        ("Netgear Workbook Parser", test_parse_netgear_workbook),
        ("Presidio Workbook Parser", test_parse_presidio_workbook),
        ("Soliton Workbook Parser", test_parse_soliton_workbook),
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
