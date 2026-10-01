import os
from typing import Any

from app.services.excel_parser.parser_models import (
    ParsedWorkbook, ParsedSheet, ParsedRecord, SheetCategory
)
from app.services.excel_parser.excel_reader import read_workbook_sheets_raw
from app.services.excel_parser.header_detector import detect_header_row
from app.services.excel_parser.column_detector import detect_column_mappings
from app.services.excel_parser.register_number_normalizer import normalize_register_number
from app.services.excel_parser.status_normalizer import normalize_candidate_status
from app.services.excel_parser.sheet_classifier import classify_sheet
from app.services.excel_parser.validation import find_sheet_anomalies, summarize_workbook_anomalies


def parse_excel_workbook(file_path: str) -> ParsedWorkbook:
    """
    Main deterministic parser entry point. Reads an Excel file and returns a structured ParsedWorkbook model.
    """
    file_name = os.path.basename(file_path)
    raw_sheets = read_workbook_sheets_raw(file_path)

    parsed_sheets: list[ParsedSheet] = []

    for sheet_name, rows in raw_sheets.items():
        if not rows:
            # Empty sheet
            parsed_sheets.append(ParsedSheet(
                sheet_name=sheet_name,
                category=SheetCategory.IGNORE,
                is_empty=True,
                warnings=["Sheet contains no rows"]
            ))
            continue

        # 1. Detect header row
        header_row_1idx, headers = detect_header_row(rows)
        header_row_0idx = header_row_1idx - 1

        data_rows = rows[header_row_1idx:]

        # 2. Detect column mapping
        col_mapping = detect_column_mappings(headers, data_rows)

        reg_col = col_mapping.get("register_number")
        name_col = col_mapping.get("student_name")
        dept_col = col_mapping.get("department")
        status_col = col_mapping.get("status")

        # Map header string to index
        header_to_idx = {h: i for i, h in enumerate(headers)}
        reg_idx = header_to_idx.get(reg_col) if reg_col else None
        name_idx = header_to_idx.get(name_col) if name_col else None
        dept_idx = header_to_idx.get(dept_col) if dept_col else None
        status_idx = header_to_idx.get(status_col) if status_col else None

        records: list[ParsedRecord] = []

        # 3. Parse data rows
        for offset, row in enumerate(data_rows):
            actual_row_idx = header_row_1idx + offset + 1

            # Ignore completely empty rows
            if not row or all(c is None or str(c).strip() == "" for c in row):
                continue

            raw_dict = {
                headers[i]: row[i] for i in range(min(len(headers), len(row))) if row[i] is not None
            }

            reg_raw = row[reg_idx] if reg_idx is not None and reg_idx < len(row) else None
            name_val = row[name_idx] if name_idx is not None and name_idx < len(row) else None
            dept_val = row[dept_idx] if dept_idx is not None and dept_idx < len(row) else None
            status_val = row[status_idx] if status_idx is not None and status_idx < len(row) else None

            # Skip row if it looks like a secondary header or empty register & name
            if reg_raw and str(reg_raw).strip().lower() in ("reg no", "register number", "roll no", "reg.no", "sl.no", "s.no"):
                continue

            # Normalize register number
            clean_reg, is_reg_valid, reg_err = normalize_register_number(reg_raw)

            # Skip row if no register number and no student name
            if not clean_reg and not name_val:
                continue

            # Normalize status
            norm_status = normalize_candidate_status(status_val)

            # Build record
            val_errors = [reg_err] if reg_err else []

            record = ParsedRecord(
                row_index=actual_row_idx,
                register_number=clean_reg,
                register_number_raw=str(reg_raw) if reg_raw is not None else None,
                is_register_valid=is_reg_valid,
                student_name=str(name_val).strip() if name_val is not None else None,
                department=str(dept_val).strip() if dept_val is not None else None,
                status=norm_status,
                validation_errors=val_errors,
                raw_values=raw_dict
            )
            records.append(record)

        # 4. Find anomalies in sheet
        duplicates, malformed = find_sheet_anomalies(records)

        # Count valid records
        valid_count = sum(1 for r in records if r.register_number and r.is_register_valid)

        # 5. Classify sheet
        category, confidence = classify_sheet(
            sheet_name,
            total_valid_records=valid_count,
            has_register_column=reg_col is not None
        )

        is_sheet_empty = len(records) == 0

        parsed_sheet = ParsedSheet(
            sheet_name=sheet_name,
            category=category,
            confidence_score=confidence,
            header_row_index=header_row_1idx,
            column_mapping=col_mapping,
            records=records,
            total_rows=len(records),
            valid_records_count=valid_count,
            duplicate_register_numbers=duplicates,
            malformed_register_numbers=malformed,
            is_empty=is_sheet_empty,
            warnings=[]
        )
        parsed_sheets.append(parsed_sheet)

    # 6. Global workbook summary
    anomalies = summarize_workbook_anomalies(parsed_sheets)

    return ParsedWorkbook(
        file_name=file_name,
        file_path=file_path,
        total_sheets=len(parsed_sheets),
        parsed_sheets=parsed_sheets,
        global_student_count=anomalies["total_valid_records"],
        global_duplicates=anomalies["global_duplicates"],
        anomalies_summary=anomalies
    )
