import logging
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import (
    Student, Company, PlacementDrive, PlacementStage,
    StudentRegistration, StudentStageResult, Placement, ImportLog
)
from app.services.excel_parser.parser_models import ParsedWorkbook, SheetCategory
from app.services.excel_parser.department_decoder import decode_department_from_register

logger = logging.getLogger(__name__)


def _resolve_department(rec_department, register_number) -> str:
    """Return department from the record, or decode it from the register number, or fall back to 'General'."""
    if rec_department and rec_department.strip():
        return rec_department.strip()
    decoded = decode_department_from_register(register_number or "")
    return decoded if decoded else "General"


def ingest_parsed_workbook(
    db: Session,
    parsed_wb: ParsedWorkbook,
    company_name: str,
    academic_year: str = "2025-2026"
) -> ImportLog:
    """
    Persists a ParsedWorkbook object into PostgreSQL database models safely and idempotently.
    Returns:
        ImportLog instance summarizing ingestion results.
    """
    # 1. Get or create Company
    company = db.scalar(select(Company).where(Company.name.ilike(company_name)))
    if not company:
        company = Company(name=company_name, industry="Technology")
        db.add(company)
        db.flush()

    # 2. Get or create Placement Drive
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
    import_details: list[dict[str, Any]] = []

    stage_order = 1

    for sheet in parsed_wb.parsed_sheets:
        if sheet.is_empty or sheet.category == SheetCategory.IGNORE:
            continue

        sheet_success = 0
        sheet_errors = 0

        # Handle Sheet Categories
        if sheet.category == SheetCategory.REGISTERED:
            for rec in sheet.records:
                if not rec.register_number or not rec.is_register_valid:
                    sheet_errors += 1
                    continue

                # Get or Create Student
                student = db.scalar(select(Student).where(Student.register_number == rec.register_number))
                resolved_dept = _resolve_department(rec.department, rec.register_number)
                if not student:
                    student = Student(
                        register_number=rec.register_number,
                        full_name=rec.student_name or "Unknown Candidate",
                        department=resolved_dept,
                        academic_year=academic_year
                    )
                    db.add(student)
                    db.flush()
                else:
                    if rec.student_name and student.full_name == "Unknown Candidate":
                        student.full_name = rec.student_name
                    if student.department == "General" and resolved_dept != "General":
                        student.department = resolved_dept

                # Get or Create Registration
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
            # Create or fetch PlacementStage
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

                # Fetch or create student
                student = db.scalar(select(Student).where(Student.register_number == rec.register_number))
                resolved_dept = _resolve_department(rec.department, rec.register_number)
                if not student:
                    student = Student(
                        register_number=rec.register_number,
                        full_name=rec.student_name or "Unknown Candidate",
                        department=resolved_dept,
                        academic_year=academic_year
                    )
                    db.add(student)
                    db.flush()
                elif student.department == "General" and resolved_dept != "General":
                    student.department = resolved_dept

                # Register student if not registered
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

                # Add stage result
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
                        status=rec.status or "QUALIFIED"
                    )
                    db.add(stage_res)
                else:
                    stage_res.status = rec.status or "QUALIFIED"

                # If PLACED category, record placement
                if sheet.category == SheetCategory.PLACED:
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
                            status="OFFERED",
                            package_ctc=6.5
                        )
                        db.add(placement)

                sheet_success += 1

        success_records += sheet_success
        error_records += sheet_errors
        import_details.append({
            "sheet_name": sheet.sheet_name,
            "category": sheet.category.value,
            "success": sheet_success,
            "errors": sheet_errors
        })

    # Create Import Log record
    log = ImportLog(
        filename=parsed_wb.file_name,
        file_type="EXCEL",
        company_id=company.id,
        drive_id=drive.id,
        total_rows=success_records + error_records,
        imported_rows=success_records,
        failed_rows=error_records,
        status="SUCCESS" if error_records == 0 else "PARTIAL_SUCCESS",
        error_details={
            "sheets": import_details,
            "global_duplicates": parsed_wb.global_duplicates
        }
    )
    db.add(log)
    db.commit()

    logger.info(f"Workbook '{parsed_wb.file_name}' ingested successfully into PostgreSQL.")
    return log
