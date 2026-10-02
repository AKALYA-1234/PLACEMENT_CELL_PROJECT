import logging
import tempfile
import os
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import (
    Student, Company, PlacementDrive, PlacementStage,
    StudentRegistration, StudentStageResult, Placement, ImportLog
)
from app.services.excel_parser.parser_engine import parse_excel_workbook
from app.services.excel_parser.parser_models import ParsedWorkbook, SheetCategory
from app.services.excel_parser.import_validation_service import validate_excel_import
from app.services.excel_parser.confirm_models import ImportConfirmResponse

logger = logging.getLogger(__name__)


def confirm_excel_import(
    file_input: str | bytes,
    file_name: str,
    company_name: str,
    academic_year: str,
    db: Session
) -> ImportConfirmResponse:
    """
    Confirms and executes database ingestion for a validated Excel workbook within an atomic database transaction.
    Requirements:
      1. Normalizes OFFER/OFFERED/ACCEPTED into PLACED.
      2. Never creates ACCEPTED as a separate status string.
      3. Uses a database transaction and rolls back everything on error.
      4. Idempotent on repeated uploads.
      5. Records detailed import_logs and statistics.
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
        # Step 1: Pre-validation check
        validation_res = validate_excel_import(
            file_input=file_to_parse,
            file_name=file_name,
            company_name=company_name,
            academic_year=academic_year,
            db=db
        )

        if not validation_res.is_valid_for_import:
            raise ValueError(
                f"Cannot confirm import: workbook contains {len(validation_res.invalid_register_numbers)} malformed register numbers."
            )

        parsed_wb: ParsedWorkbook = parse_excel_workbook(file_to_parse)

        # Step 2: Atomic Transaction Ingestion
        try:
            # Get or Create Company
            company = db.scalar(select(Company).where(Company.name.ilike(company_name)))
            if not company:
                company = Company(name=company_name, industry="Technology")
                db.add(company)
                db.flush()

            # Get or Create Placement Drive
            drive_name = f"{company.name} Drive {academic_year}"
            drive = db.scalar(
                select(PlacementDrive).where(
                    PlacementDrive.company_id == company.id,
                    PlacementDrive.drive_name == drive_name,
                    PlacementDrive.academic_year == academic_year
                )
            )
            if not drive:
                drive = PlacementDrive(
                    company_id=company.id,
                    drive_name=drive_name,
                    academic_year=academic_year,
                    status="ACTIVE"
                )
                db.add(drive)
                db.flush()

            success_records = 0
            error_records = 0
            sheet_stats: list[dict[str, Any]] = []

            stage_order = 1

            for sheet in parsed_wb.parsed_sheets:
                if sheet.is_empty or sheet.category == SheetCategory.IGNORE:
                    continue

                sheet_success = 0
                sheet_errors = 0

                if sheet.category == SheetCategory.REGISTERED:
                    for rec in sheet.records:
                        if not rec.register_number or not rec.is_register_valid:
                            sheet_errors += 1
                            continue

                        # Fetch or Create Student
                        student = db.scalar(select(Student).where(Student.register_number == rec.register_number))
                        if not student:
                            student = Student(
                                register_number=rec.register_number,
                                full_name=rec.student_name or "Unknown Candidate",
                                department=rec.department or "General",
                                academic_year=academic_year
                            )
                            db.add(student)
                            db.flush()
                        else:
                            if rec.student_name and student.full_name == "Unknown Candidate":
                                student.full_name = rec.student_name
                            if rec.department and student.department == "General":
                                student.department = rec.department

                        # Fetch or Create Registration
                        reg = db.scalar(
                            select(StudentRegistration).where(
                                StudentRegistration.student_id == student.id,
                                StudentRegistration.drive_id == drive.id
                            )
                        )
                        if not reg:
                            reg = StudentRegistration(
                                student_id=student.id,
                                drive_id=drive.id,
                                is_eligible=True
                            )
                            db.add(reg)
                            db.flush()

                        sheet_success += 1

                elif sheet.category in (SheetCategory.PROGRESSION, SheetCategory.PLACED):
                    stage = db.scalar(
                        select(PlacementStage).where(
                            PlacementStage.drive_id == drive.id,
                            PlacementStage.stage_name == sheet.sheet_name
                        )
                    )
                    if not stage:
                        stage = PlacementStage(
                            drive_id=drive.id,
                            stage_name=sheet.sheet_name,
                            stage_order=stage_order,
                            normalized_category=sheet.category.value
                        )
                        db.add(stage)
                        db.flush()
                        stage_order += 1

                    for rec in sheet.records:
                        if not rec.register_number or not rec.is_register_valid:
                            sheet_errors += 1
                            continue

                        student = db.scalar(select(Student).where(Student.register_number == rec.register_number))
                        if not student:
                            student = Student(
                                register_number=rec.register_number,
                                full_name=rec.student_name or "Unknown Candidate",
                                department=rec.department or "General",
                                academic_year=academic_year
                            )
                            db.add(student)
                            db.flush()

                        reg = db.scalar(
                            select(StudentRegistration).where(
                                StudentRegistration.student_id == student.id,
                                StudentRegistration.drive_id == drive.id
                            )
                        )
                        if not reg:
                            reg = StudentRegistration(
                                student_id=student.id,
                                drive_id=drive.id,
                                is_eligible=True
                            )
                            db.add(reg)
                            db.flush()

                        # Normalize Stage Status
                        raw_status = (rec.status or "QUALIFIED").upper()
                        if raw_status in ("OFFER", "OFFERED", "ACCEPTED", "PLACED"):
                            normalized_status = "QUALIFIED"  # Stage result status
                        else:
                            normalized_status = raw_status

                        stage_res = db.scalar(
                            select(StudentStageResult).where(
                                StudentStageResult.registration_id == reg.id,
                                StudentStageResult.stage_id == stage.id
                            )
                        )
                        if not stage_res:
                            stage_res = StudentStageResult(
                                stage_id=stage.id,
                                student_id=student.id,
                                registration_id=reg.id,
                                status=normalized_status
                            )
                            db.add(stage_res)
                        else:
                            stage_res.status = normalized_status

                        # Rule 7 & 8: Normalize OFFER / OFFERED / ACCEPTED -> PLACED
                        if sheet.category == SheetCategory.PLACED or raw_status in ("OFFER", "OFFERED", "ACCEPTED", "PLACED"):
                            placement = db.scalar(
                                select(Placement).where(
                                    Placement.student_id == student.id,
                                    Placement.drive_id == drive.id
                                )
                            )
                            if not placement:
                                placement = Placement(
                                    student_id=student.id,
                                    drive_id=drive.id,
                                    registration_id=reg.id,
                                    stage_id=stage.id,
                                    status="PLACED",  # Always normalize OFFER/OFFERED/ACCEPTED to PLACED
                                    package_ctc=6.5
                                )
                                db.add(placement)
                            else:
                                placement.status = "PLACED"

                        sheet_success += 1

                success_records += sheet_success
                error_records += sheet_errors
                sheet_stats.append({
                    "sheet_name": sheet.sheet_name,
                    "category": sheet.category.value,
                    "success": sheet_success,
                    "errors": sheet_errors
                })

            # Save Import Log
            log = ImportLog(
                filename=file_name,
                file_type="EXCEL",
                company_id=company.id,
                drive_id=drive.id,
                total_rows=success_records + error_records,
                imported_rows=success_records,
                failed_rows=error_records,
                status="SUCCESS" if error_records == 0 else "PARTIAL_SUCCESS",
                error_details={
                    "sheet_statistics": sheet_stats,
                    "registered_count": validation_res.registered_count,
                    "progression_count": validation_res.progression_count,
                    "placed_count": validation_res.placed_count,
                    "global_duplicates": parsed_wb.global_duplicates
                }
            )
            db.add(log)
            db.commit()

            return ImportConfirmResponse(
                status="SUCCESS",
                message=f"Workbook '{file_name}' imported into PostgreSQL successfully.",
                import_log_id=log.id,
                company_id=company.id,
                drive_id=drive.id,
                company_name=company.name,
                drive_name=drive.drive_name,
                academic_year=academic_year,
                total_records_processed=success_records + error_records,
                imported_records_count=success_records,
                failed_records_count=error_records,
                statistics={
                    "registered_count": validation_res.registered_count,
                    "progression_count": validation_res.progression_count,
                    "placed_count": validation_res.placed_count,
                    "sheets_processed": len(sheet_stats)
                }
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Transaction failed during import confirm: {e}")
            raise e

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
