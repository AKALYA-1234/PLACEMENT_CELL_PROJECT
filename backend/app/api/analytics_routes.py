from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, distinct, desc

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
    """Retrieves top-level placement dashboard KPIs and overview metrics."""
    student_query = select(func.count(Student.id))
    placement_query = select(func.count(distinct(Placement.student_id)))
    company_query = select(func.count(Company.id))
    drive_query = select(func.count(PlacementDrive.id))
    avg_ctc_query = select(func.avg(Placement.package_ctc))
    max_ctc_query = select(func.max(Placement.package_ctc))

    if academic_year:
        student_query = student_query.where(Student.academic_year == academic_year)
        placement_query = placement_query.join(Student, Placement.student_id == Student.id).where(Student.academic_year == academic_year)
        drive_query = drive_query.where(PlacementDrive.academic_year == academic_year)

    total_students = db.scalar(student_query) or 0
    total_placed = db.scalar(placement_query) or 0
    unplaced_students = max(0, total_students - total_placed)
    placement_rate = round((total_placed / total_students * 100), 2) if total_students > 0 else 0.0

    total_companies = db.scalar(company_query) or 0
    total_drives = db.scalar(drive_query) or 0

    avg_ctc_val = db.scalar(avg_ctc_query)
    avg_ctc = round(float(avg_ctc_val), 2) if avg_ctc_val else 0.0

    max_ctc_val = db.scalar(max_ctc_query)
    highest_ctc = float(max_ctc_val) if max_ctc_val else 0.0

    return {
        "academic_year": academic_year or "All Years",
        "total_students": total_students,
        "total_placed": total_placed,
        "unplaced_students": unplaced_students,
        "placement_rate_percentage": placement_rate,
        "total_companies": total_companies,
        "total_drives": total_drives,
        "average_ctc_lpa": avg_ctc,
        "highest_ctc_lpa": highest_ctc
    }


@router.get("/departments")
async def get_analytics_departments_endpoint(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves department-wise placement statistics breakdown."""
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

        ctc_query = select(func.avg(Placement.package_ctc))\
            .join(Student, Placement.student_id == Student.id)\
            .where(Student.department == dept_name)

        if academic_year:
            pl_query = pl_query.where(Student.academic_year == academic_year)
            ctc_query = ctc_query.where(Student.academic_year == academic_year)

        placed_st = db.scalar(pl_query) or 0
        unplaced_st = max(0, total_st - placed_st)
        rate = round((placed_st / total_st * 100), 2) if total_st > 0 else 0.0

        avg_ctc_val = db.scalar(ctc_query)
        avg_ctc = round(float(avg_ctc_val), 2) if avg_ctc_val else 0.0

        departments_list.append({
            "department": dept_name,
            "total_students": total_st,
            "placed_students": placed_st,
            "unplaced_students": unplaced_st,
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
    """Retrieves company-wise placement comparison, offers count, and CTC metrics."""
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

        max_ctc = db.scalar(
            select(func.max(Placement.package_ctc))
            .where(Placement.drive_id.in_(drive_ids))
        )

        companies_stats.append({
            "company_id": c.id,
            "company_name": c.name,
            "industry": c.industry,
            "drives_count": len(drive_ids),
            "registered_candidates": total_registered,
            "placed_candidates": total_placed,
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
    """Retrieves round/stage candidate progression and drop-off funnel analytics."""
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
