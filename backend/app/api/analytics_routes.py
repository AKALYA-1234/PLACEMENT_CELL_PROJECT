from typing import Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, distinct, case

from app.database import get_db
from app.models.admin_user import AdminUser
from app.models import Student, Company, PlacementDrive, PlacementStage, StudentRegistration, StudentStageResult, Placement
from app.utils.security import get_current_admin

router = APIRouter(prefix="/admin/analytics", tags=["Admin Analytics"])


@router.get("/overview")
async def get_analytics_overview_endpoint(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves deterministic overall college placement metrics using SQL aggregations."""
    student_q = select(func.count(Student.id))
    company_q = select(func.count(Company.id))
    drive_q = select(func.count(PlacementDrive.id))
    registration_q = select(func.count(StudentRegistration.id))
    placement_record_q = select(func.count(Placement.id))
    placed_student_q = select(func.count(distinct(Placement.student_id)))
    avg_ctc_q = select(func.avg(Placement.package_ctc))
    max_ctc_q = select(func.max(Placement.package_ctc))

    if academic_year:
        student_q = student_q.where(Student.academic_year == academic_year)
        drive_q = drive_q.where(PlacementDrive.academic_year == academic_year)
        registration_q = registration_q.join(PlacementDrive, StudentRegistration.drive_id == PlacementDrive.id)\
            .where(PlacementDrive.academic_year == academic_year)
        placement_record_q = placement_record_q.join(PlacementDrive, Placement.drive_id == PlacementDrive.id)\
            .where(PlacementDrive.academic_year == academic_year)
        placed_student_q = placed_student_q.join(Student, Placement.student_id == Student.id)\
            .where(Student.academic_year == academic_year)

    total_students = db.scalar(student_q) or 0
    total_companies = db.scalar(company_q) or 0
    total_drives = db.scalar(drive_q) or 0
    total_registrations = db.scalar(registration_q) or 0
    total_placement_records = db.scalar(placement_record_q) or 0
    students_placed = db.scalar(placed_student_q) or 0

    registered_students = db.scalar(
        select(func.count(distinct(StudentRegistration.student_id)))
    ) or 0

    students_not_placed = max(0, total_students - students_placed)
    placement_rate = round((students_placed / total_students * 100), 2) if total_students > 0 else 0.0

    avg_ctc_val = db.scalar(avg_ctc_q)
    avg_ctc = round(float(avg_ctc_val), 2) if avg_ctc_val else 0.0

    max_ctc_val = db.scalar(max_ctc_q)
    highest_ctc = float(max_ctc_val) if max_ctc_val else 0.0

    return {
        "academic_year": academic_year or "All Years",
        "total_students": total_students,
        "total_companies": total_companies,
        "total_drives": total_drives,
        "total_registrations": total_registrations,
        "total_placement_records": total_placement_records,
        "students_placed": students_placed,
        "total_placed": students_placed,
        "students_not_placed": students_not_placed,
        "unplaced_students": students_not_placed,
        "placement_rate_percentage": placement_rate,
        "average_ctc_lpa": avg_ctc,
        "highest_ctc_lpa": highest_ctc
    }


@router.get("/departments")
async def get_analytics_departments_endpoint(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves department-wise SQL aggregated statistics breakdown."""
    query = select(
        Student.department,
        func.count(distinct(Student.id)).label("total_students")
    )
    if academic_year:
        query = query.where(Student.academic_year == academic_year)

    query = query.group_by(Student.department)
    dept_rows = db.execute(query).all()

    departments_list = []
    for dept_name, total_st in dept_rows:
        pl_query = select(func.count(distinct(Placement.student_id)))\
            .join(Student, Placement.student_id == Student.id)\
            .where(Student.department == dept_name)

        reg_query = select(func.count(distinct(StudentRegistration.student_id)))\
            .join(Student, StudentRegistration.student_id == Student.id)\
            .where(Student.department == dept_name)

        ctc_query = select(func.avg(Placement.package_ctc))\
            .join(Student, Placement.student_id == Student.id)\
            .where(Student.department == dept_name)

        if academic_year:
            pl_query = pl_query.where(Student.academic_year == academic_year)
            reg_query = reg_query.where(Student.academic_year == academic_year)
            ctc_query = ctc_query.where(Student.academic_year == academic_year)

        placed_st = db.scalar(pl_query) or 0
        reg_st = db.scalar(reg_query) or 0
        not_placed_st = max(0, total_st - placed_st)
        rate = round((placed_st / total_st * 100), 2) if total_st > 0 else 0.0

        avg_ctc_val = db.scalar(ctc_query)
        avg_ctc = round(float(avg_ctc_val), 2) if avg_ctc_val else 0.0

        departments_list.append({
            "department": dept_name,
            "total_students": total_st,
            "placed_students": placed_st,
            "not_placed_students": not_placed_st,
            "placement_rate_percentage": rate,
            "average_ctc_lpa": avg_ctc
        })

    return {
        "total_departments": len(departments_list),
        "departments": departments_list
    }


@router.get("/companies")
async def get_analytics_companies_endpoint(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves company-wise candidate participation, placement, and CTC SQL metrics."""
    companies = db.scalars(select(Company).order_by(Company.name.asc())).all()

    companies_stats = []
    for c in companies:
        drive_q = select(PlacementDrive.id).where(PlacementDrive.company_id == c.id)
        if academic_year:
            drive_q = drive_q.where(PlacementDrive.academic_year == academic_year)

        drive_ids = db.scalars(drive_q).all()
        if not drive_ids:
            continue

        total_registered = db.scalar(
            select(func.count(distinct(StudentRegistration.student_id)))
            .where(StudentRegistration.drive_id.in_(drive_ids))
        ) or 0

        total_placed = db.scalar(
            select(func.count(distinct(Placement.student_id)))
            .where(Placement.drive_id.in_(drive_ids))
        ) or 0

        unplaced_count = max(0, total_registered - total_placed)

        max_ctc = db.scalar(
            select(func.max(Placement.package_ctc))
            .where(Placement.drive_id.in_(drive_ids))
        )

        companies_stats.append({
            "company_id": c.id,
            "company_name": c.name,
            "industry": c.industry,
            "drives_count": len(drive_ids),
            "registered_students": total_registered,
            "unplaced_counts": unplaced_count,
            "progression_counts": unplaced_count,
            "placed_students": total_placed,
            "max_ctc_lpa": float(max_ctc) if max_ctc else 0.0
        })

    return {
        "total_companies": len(companies_stats),
        "companies": companies_stats
    }


@router.get("/rounds")
async def get_analytics_rounds_endpoint(
    company_id: Optional[int] = Query(None, description="Filter round analytics by specific company ID"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves round/stage candidate progression and drop-off funnel analytics via SQL."""
    stage_query = select(PlacementStage)
    if company_id:
        d_ids = db.scalars(select(PlacementDrive.id).where(PlacementDrive.company_id == company_id)).all()
        stage_query = stage_query.where(PlacementStage.drive_id.in_(d_ids))

    stages = db.scalars(stage_query.order_by(PlacementStage.stage_order.asc())).all()

    rounds_data = []
    for s in stages:
        qualified_count = db.scalar(
            select(func.count(StudentStageResult.id))
            .where(StudentStageResult.stage_id == s.id, StudentStageResult.status == "QUALIFIED")
        ) or 0

        total_participants = db.scalar(
            select(func.count(StudentStageResult.id))
            .where(StudentStageResult.stage_id == s.id)
        ) or 0

        rounds_data.append({
            "stage_id": s.id,
            "drive_id": s.drive_id,
            "stage_name": s.stage_name,
            "stage_order": s.stage_order,
            "category": s.normalized_category,
            "total_participants": total_participants,
            "qualified_count": qualified_count,
            "drop_off_count": max(0, total_participants - qualified_count)
        })

    return {
        "total_stages_analyzed": len(rounds_data),
        "rounds": rounds_data
    }


@router.get("/student/{register_number}")
async def get_student_analytics_endpoint(
    register_number: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves student-specific analytics: registered, unplaced, placed companies, highest round per company, overall status."""
    student = db.scalar(select(Student).where(Student.register_number == register_number))
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with register number '{register_number}' not found."
        )

    registrations = db.scalars(
        select(StudentRegistration).where(StudentRegistration.student_id == student.id)
    ).all()

    placements = db.scalars(
        select(Placement).where(Placement.student_id == student.id)
    ).all()

    placed_drive_ids = {p.drive_id for p in placements}

    company_breakdown = []
    registered_companies = 0
    unplaced_companies = 0
    placed_companies = 0

    for reg in registrations:
        drive = db.scalar(select(PlacementDrive).where(PlacementDrive.id == reg.drive_id))
        company = db.scalar(select(Company).where(Company.id == drive.company_id)) if drive else None
        company_name = company.name if company else f"Drive #{reg.drive_id}"

        stage_results = db.scalars(
            select(StudentStageResult)
            .where(StudentStageResult.student_id == student.id, StudentStageResult.stage_id.in_(
                select(PlacementStage.id).where(PlacementStage.drive_id == reg.drive_id)
            ))
        ).all()

        max_round = 0
        for sr in stage_results:
            stage = db.scalar(select(PlacementStage).where(PlacementStage.id == sr.stage_id))
            if stage and sr.status == "QUALIFIED":
                max_round = max(max_round, stage.stage_order)

        is_placed = reg.drive_id in placed_drive_ids
        registered_companies += 1

        if is_placed:
            placed_companies += 1
            c_status = "PLACED"
        else:
            unplaced_companies += 1
            c_status = "NOT PLACED"

        company_breakdown.append({
            "drive_id": reg.drive_id,
            "company_name": company_name,
            "highest_round_reached": max_round,
            "status": c_status
        })

    overall_status = "PLACED" if len(placements) > 0 else "UNPLACED"

    return {
        "register_number": student.register_number,
        "full_name": student.full_name,
        "department": student.department,
        "cgpa": student.cgpa,
        "overall_status": overall_status,
        "registered_companies": registered_companies,
        "unplaced_companies": unplaced_companies,
        "progression_companies": unplaced_companies,
        "placed_companies": placed_companies,
        "company_breakdown": company_breakdown
    }
