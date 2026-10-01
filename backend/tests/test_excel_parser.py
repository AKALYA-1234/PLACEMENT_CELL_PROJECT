import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.services.excel_parser import (
    parse_excel_workbook, SheetCategory, ParsedWorkbook
)
from app.services.excel_parser.register_number_normalizer import normalize_register_number
from app.services.excel_parser.status_normalizer import normalize_candidate_status

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data"))


def test_register_number_normalizer():
    # Standard valid
    clean, valid, err = normalize_register_number("7376231cs333 ")
    assert clean == "7376231CS333"
    assert valid is True
    assert err is None

    # Float conversion
    clean, valid, err = normalize_register_number(73762310101.0)
    assert clean == "73762310101"

    # Malformed phone number
    clean, valid, err = normalize_register_number("8667022811")
    assert valid is False
    assert "phone number" in err

    # Malformed batch year
    clean, valid, err = normalize_register_number("7377231CS289")
    assert valid is False
    assert "invalid batch" in err

    # Empty
    clean, valid, err = normalize_register_number("  ")
    assert clean is None
    assert valid is False


def test_status_normalizer():
    assert normalize_candidate_status("AB") == "ABSENT"
    assert normalize_candidate_status("Absent") == "ABSENT"
    assert normalize_candidate_status("Qualified") == "QUALIFIED"
    assert normalize_candidate_status("Selected") == "QUALIFIED"
    assert normalize_candidate_status("Placed") == "OFFERED"
    assert normalize_candidate_status("Accepted") == "ACCEPTED"


def test_parse_netgear_workbook():
    file_path = os.path.join(SAMPLE_DIR, "Netgear - Roundwise.xlsx")
    assert os.path.exists(file_path), f"Sample file not found: {file_path}"

    workbook: ParsedWorkbook = parse_excel_workbook(file_path)

    assert workbook.file_name == "Netgear - Roundwise.xlsx"
    assert workbook.total_sheets == 4

    # Check Sheet 1 (Registered)
    sheet1 = workbook.parsed_sheets[0]
    assert sheet1.category == SheetCategory.REGISTERED
    assert sheet1.header_row_index == 1
    assert sheet1.valid_records_count == 333
    # Netgear sheet 1 has 2 malformed records
    assert len(sheet1.malformed_register_numbers) == 2

    # Check Sheet 3 (Round 3 - Header Offset Row 3)
    sheet3 = workbook.parsed_sheets[2]
    assert sheet3.category == SheetCategory.PROGRESSION
    assert sheet3.header_row_index == 3
    assert sheet3.valid_records_count == 10

    # Check Sheet 4 (Round 4 - Selects List)
    sheet4 = workbook.parsed_sheets[3]
    assert sheet4.category == SheetCategory.PROGRESSION
    assert sheet4.header_row_index == 3  # Detected row 3 offset!
    assert sheet4.valid_records_count == 2
    placed_regs = [r.register_number for r in sheet4.records if r.is_register_valid]
    assert "7376231CS313" in placed_regs
    assert "7376231EC134" in placed_regs


def test_parse_presidio_workbook():
    file_path = os.path.join(SAMPLE_DIR, "PRESIDIO.xlsx")
    assert os.path.exists(file_path), f"Sample file not found: {file_path}"

    workbook: ParsedWorkbook = parse_excel_workbook(file_path)

    assert workbook.file_name == "PRESIDIO.xlsx"
    assert workbook.total_sheets == 3

    # Sheet 1: Round 1 (Progression)
    sheet1 = workbook.parsed_sheets[0]
    assert sheet1.category == SheetCategory.PROGRESSION
    assert sheet1.valid_records_count == 419

    # Sheet 3 (index 2): offer (Placed)
    sheet3 = workbook.parsed_sheets[2]
    assert sheet3.category == SheetCategory.PLACED
    assert sheet3.valid_records_count == 3


def test_parse_soliton_workbook():
    file_path = os.path.join(SAMPLE_DIR, "Soliton Roundwise Details.xlsx")
    assert os.path.exists(file_path), f"Sample file not found: {file_path}"

    workbook: ParsedWorkbook = parse_excel_workbook(file_path)

    assert workbook.file_name == "Soliton Roundwise Details.xlsx"
    assert workbook.total_sheets == 7

    # Check OFFER List sheet
    offer_sheet = [s for s in workbook.parsed_sheets if "OFFER" in s.sheet_name][0]
    assert offer_sheet.category == SheetCategory.PLACED
    assert offer_sheet.valid_records_count == 7

    round1_sheet = workbook.parsed_sheets[0]
    assert round1_sheet.valid_records_count == 520

if __name__ == "__main__":
    pytest.main(["-v", __file__])
