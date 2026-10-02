import tempfile
import os
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import Student
from app.services.excel_parser.parser_engine import parse_excel_workbook
from app.services.excel_parser.parser_models import SheetCategory, ParsedWorkbook
from app.services.excel_parser.validation_models import (
    ImportValidationResponse, SheetValidationSummary, ValidationConflict
)


def validate_excel_import(
    file_input: str | bytes,
    file_name: str,
    company_name: str,
    academic_year: str,
    db: Session | None = None
) -> ImportValidationResponse:
    """
    Validates an Excel workbook file against normalization rules and database master records without mutating PostgreSQL data.
    """
    temp_path = None
    if isinstance(file_input, bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(file_input)
            temp_path = tmp.name
        file_to_parse = temp_path
    else:
        file_to_parse = file_input

    try:
        parsed_wb: ParsedWorkbook = parse_excel_workbook(file_to_parse)

        detected_sheets: list[SheetValidationSummary] = []
        registered_count = 0
        progression_count = 0
        placed_count = 0
        unknown_sheets_count = 0
        total_records_count = 0

        missing_regs: list[dict[str, Any]] = []
        invalid_regs: list[dict[str, Any]] = []
        conflicts: list[ValidationConflict] = []
        all_valid_regs: set[str] = set()

        for sheet in parsed_wb.parsed_sheets:
            if sheet.is_empty or sheet.category == SheetCategory.IGNORE:
                continue

            if sheet.category == SheetCategory.REGISTERED:
                registered_count += sheet.valid_records_count
            elif sheet.category == SheetCategory.PROGRESSION:
                progression_count += sheet.valid_records_count
            elif sheet.category == SheetCategory.PLACED:
                placed_count += sheet.valid_records_count
            else:
                unknown_sheets_count += 1

            total_records_count += sheet.total_rows

            # Sample records preview for UI
            samples = [
                {
                    "row_index": r.row_index,
                    "register_number": r.register_number,
                    "student_name": r.student_name,
                    "department": r.department,
                    "status": r.status
                }
                for r in sheet.records[:5]
            ]

            summary = SheetValidationSummary(
                sheet_name=sheet.sheet_name,
                category=sheet.category,
                header_row_index=sheet.header_row_index,
                total_records=sheet.total_rows,
                valid_records_count=sheet.valid_records_count,
                malformed_count=len(sheet.malformed_register_numbers),
                duplicate_count=len(sheet.duplicate_register_numbers),
                column_mapping=sheet.column_mapping,
                sample_records=samples
            )
            detected_sheets.append(summary)

            # Record level checks
            for record in sheet.records:
                if not record.register_number:
                    missing_regs.append({
                        "sheet_name": sheet.sheet_name,
                        "row_index": record.row_index,
                        "raw_name": record.student_name
                    })
                    conflicts.append(ValidationConflict(
                        severity="WARNING",
                        conflict_type="MISSING_REGISTER_NUMBER",
                        sheet_name=sheet.sheet_name,
                        row_index=record.row_index,
                        message=f"Missing register number at row {record.row_index} in sheet '{sheet.sheet_name}'"
                    ))
                elif not record.is_register_valid:
                    invalid_regs.append({
                        "sheet_name": sheet.sheet_name,
                        "row_index": record.row_index,
                        "raw_val": record.register_number_raw,
                        "register_number": record.register_number,
                        "errors": record.validation_errors
                    })
                    conflicts.append(ValidationConflict(
                        severity="ERROR",
                        conflict_type="MALFORMED_REGISTER",
                        sheet_name=sheet.sheet_name,
                        row_index=record.row_index,
                        register_number=record.register_number,
                        message=f"Malformed register number '{record.register_number_raw}' at row {record.row_index}"
                    ))
                else:
                    all_valid_regs.add(record.register_number)

            # Duplicate conflicts
            for dup in sheet.duplicate_register_numbers:
                conflicts.append(ValidationConflict(
                    severity="WARNING",
                    conflict_type="DUPLICATE_REGISTER",
                    sheet_name=sheet.sheet_name,
                    register_number=dup,
                    message=f"Duplicate register number '{dup}' within sheet '{sheet.sheet_name}'"
                ))

        # Check master student DB table if DB session provided
        students_not_in_master: list[str] = []
        if db and all_valid_regs:
            existing_regs_query = select(Student.register_number).where(Student.register_number.in_(all_valid_regs))
            existing_regs = set(db.scalars(existing_regs_query).all())
            missing_in_db = sorted(all_valid_regs - existing_regs)
            students_not_in_master = missing_in_db

            for reg in missing_in_db:
                conflicts.append(ValidationConflict(
                    severity="INFO",
                    conflict_type="MISSING_STUDENT_IN_MASTER",
                    register_number=reg,
                    message=f"Register number '{reg}' not found in master Student table (will be auto-created on import)"
                ))

        is_valid = len(invalid_regs) == 0

        return ImportValidationResponse(
            company_name=company_name,
            academic_year=academic_year,
            file_name=file_name,
            total_sheets=parsed_wb.total_sheets,
            detected_sheets=detected_sheets,
            total_records_count=total_records_count,
            registered_count=registered_count,
            progression_count=progression_count,
            placed_count=placed_count,
            unknown_sheets_count=unknown_sheets_count,
            missing_register_numbers=missing_regs,
            invalid_register_numbers=invalid_regs,
            duplicate_register_numbers=parsed_wb.global_duplicates,
            students_not_found_in_master=students_not_in_master,
            possible_conflicts=conflicts,
            is_valid_for_import=is_valid
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
