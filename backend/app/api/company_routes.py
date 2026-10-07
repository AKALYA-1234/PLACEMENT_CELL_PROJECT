from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, exists, not_

from app.database import get_db
from app.models.admin_user import AdminUser
from app.models import Company, PlacementDrive, PlacementStage, StudentRegistration, StudentStageResult, Placement, Student
# TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
# In demo mode, get_current_admin returns a demo admin when no token is present.
from app.utils.security import get_current_admin

router = APIRouter(prefix="/admin/companies", tags=["Admin Companies"])


@router.get("")
async def list_companies_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by company name or industry"),
    placement_status: Optional[str] = Query(None, alias="status", description="Filter: PLACED, NON_PLACED, or REGISTERED"),
    department: Optional[str] = Query(None, description="Filter by participating student department"),
    round_name: Optional[str] = Query(None, description="Filter by placement round/stage name"),
    academic_year: Optional[str] = Query(None, description="Filter by drive academic year"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves paginated list of companies with placement metrics."""
    query = select(Company)
    if search:
        query = query.where(
            or_(
                Company.name.ilike(f"%{search}%"),
                Company.industry.ilike(f"%{search}%")
            )
        )

    if industry:
        query = query.where(Company.industry.ilike(f"%{industry}%"))

    company_drives = select(PlacementDrive.id).where(PlacementDrive.company_id == Company.id)
    registered_exists = exists(
        select(StudentRegistration.id).where(StudentRegistration.drive_id.in_(company_drives))
    )
    placed_exists = exists(
        select(Placement.id).where(Placement.drive_id.in_(company_drives))
    )

    if academic_year:
        query = query.where(
            exists(
                select(PlacementDrive.id).where(
                    PlacementDrive.company_id == Company.id,
                    PlacementDrive.academic_year == academic_year,
                )
            )
        )

    if department:
        query = query.where(
            exists(
                select(StudentRegistration.id)
                .join(Student, Student.id == StudentRegistration.student_id)
                .join(PlacementDrive, PlacementDrive.id == StudentRegistration.drive_id)
                .where(
                    PlacementDrive.company_id == Company.id,
                    Student.department == department,
                )
            )
        )

    if round_name:
        query = query.where(
            exists(
                select(PlacementStage.id)
                .join(PlacementDrive, PlacementDrive.id == PlacementStage.drive_id)
                .where(
                    PlacementDrive.company_id == Company.id,
                    PlacementStage.stage_name == round_name,
                )
            )
        )

    if placement_status:
        normalized_status = placement_status.upper()
        if normalized_status == "PLACED":
            query = query.where(placed_exists)
        elif normalized_status == "REGISTERED":
            query = query.where(registered_exists)
        elif normalized_status in ("NON_PLACED", "NOT_PLACED", "UNPLACED"):
            query = query.where(registered_exists, not_(placed_exists))

    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    offset = (page - 1) * limit
    companies = db.scalars(query.order_by(Company.name.asc()).offset(offset).limit(limit)).all()

    items = []
    for c in companies:
        drives = db.scalars(select(PlacementDrive).where(PlacementDrive.company_id == c.id)).all()
        drive_ids = [d.id for d in drives]

        total_registered = 0
        total_placed = 0
        if drive_ids:
            total_registered = db.scalar(
                select(func.count(func.distinct(StudentRegistration.student_id)))
                .where(StudentRegistration.drive_id.in_(drive_ids))
            ) or 0

            total_placed = db.scalar(
                select(func.count(func.distinct(Placement.student_id)))
                .where(Placement.drive_id.in_(drive_ids))
            ) or 0

        items.append({
            "id": c.id,
            "name": c.name,
            "industry": c.industry,
            "website": c.website,
            "contact_email": c.contact_email,
            "drives_count": len(drives),
            "total_registered": total_registered,
            "total_placed": total_placed
        })

    pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "filter_options": {
            "departments": db.scalars(
                select(Student.department)
                .where(Student.department.is_not(None), Student.department != "")
                .distinct()
                .order_by(Student.department.asc())
            ).all(),
            "rounds": db.scalars(
                select(PlacementStage.stage_name)
                .where(PlacementStage.stage_name.is_not(None), PlacementStage.stage_name != "")
                .distinct()
                .order_by(PlacementStage.stage_name.asc())
            ).all(),
            "academic_years": db.scalars(
                select(PlacementDrive.academic_year)
                .where(PlacementDrive.academic_year.is_not(None), PlacementDrive.academic_year != "")
                .distinct()
                .order_by(PlacementDrive.academic_year.desc())
            ).all(),
        }
    }


@router.get("/{company_id}")
async def get_company_detail_endpoint(
    company_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves detailed profile for a specific company and its placement drives."""
    company = db.scalar(select(Company).where(Company.id == company_id))
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found."
        )

    drives = db.scalars(
        select(PlacementDrive)
        .where(PlacementDrive.company_id == company.id)
        .order_by(PlacementDrive.drive_date.desc())
    ).all()

    drives_data = []
    for d in drives:
        reg_count = db.scalar(
            select(func.count(StudentRegistration.id)).where(StudentRegistration.drive_id == d.id)
        ) or 0

        placed_count = db.scalar(
            select(func.count(Placement.id)).where(Placement.drive_id == d.id)
        ) or 0

        drives_data.append({
            "id": d.id,
            "drive_name": d.drive_name,
            "academic_year": d.academic_year,
            "job_role": d.job_role,
            "ctc_lpa": d.ctc_lpa,
            "drive_date": d.drive_date.isoformat() if d.drive_date else None,
            "status": d.status,
            "registered_count": reg_count,
            "placed_count": placed_count
        })

    return {
        "id": company.id,
        "name": company.name,
        "industry": company.industry,
        "website": company.website,
        "contact_email": company.contact_email,
        "drives": drives_data
    }


@router.get("/{company_id}/students")
async def get_company_students_endpoint(
    company_id: int,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by candidate status: PLACED / REGISTERED"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves unique candidates participating in or placed by drives of a specific company."""
    company = db.scalar(select(Company).where(Company.id == company_id))
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found."
        )

    drive_ids = db.scalars(select(PlacementDrive.id).where(PlacementDrive.company_id == company.id)).all()
    if not drive_ids:
        return {"items": [], "total": 0, "page": page, "limit": limit, "pages": 1}

    if status_filter and status_filter.upper() == "PLACED":
        # Select unique placed students
        subq = (
            select(Placement.student_id, func.max(Placement.package_ctc).label("max_ctc"))
            .where(Placement.drive_id.in_(drive_ids))
            .group_by(Placement.student_id)
            .subquery()
        )
        query = (
            select(Student, subq.c.max_ctc)
            .join(subq, Student.id == subq.c.student_id)
            .order_by(Student.register_number.asc())
        )
    else:
        # Select unique registered students
        subq = (
            select(StudentRegistration.student_id)
            .where(StudentRegistration.drive_id.in_(drive_ids))
            .distinct()
            .subquery()
        )
        query = (
            select(Student)
            .join(subq, Student.id == subq.c.student_id)
            .order_by(Student.register_number.asc())
        )

    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    offset = (page - 1) * limit
    results = db.execute(query.offset(offset).limit(limit)).all()

    items = []
    for row in results:
        if status_filter and status_filter.upper() == "PLACED":
            student = row[0]
            max_ctc = row[1]
        else:
            student = row[0]
            max_ctc = None

        placement = db.scalar(
            select(Placement).where(Placement.student_id == student.id, Placement.drive_id.in_(drive_ids))
        )

        items.append({
            "student_id": student.id,
            "register_number": student.register_number,
            "full_name": student.full_name,
            "department": student.department,
            "drive_name": company.name + " Campus Drive",
            "is_placed": placement is not None,
            "package_ctc": placement.package_ctc if placement else max_ctc
        })

    pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


@router.get("/{company_id}/statistics")
async def get_company_statistics_endpoint(
    company_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves aggregated placement funnel statistics for a specific company."""
    company = db.scalar(select(Company).where(Company.id == company_id))
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found."
        )

    drives = db.scalars(select(PlacementDrive).where(PlacementDrive.company_id == company.id)).all()
    drive_ids = [d.id for d in drives]

    if not drive_ids:
        return {
            "company_id": company.id,
            "company_name": company.name,
            "total_drives": 0,
            "registered_candidates": 0,
            "placed_candidates": 0,
            "selection_rate_percentage": 0.0,
            "stages_breakdown": []
        }

    total_registered = db.scalar(
        select(func.count(func.distinct(StudentRegistration.student_id)))
        .where(StudentRegistration.drive_id.in_(drive_ids))
    ) or 0

    total_placed = db.scalar(
        select(func.count(func.distinct(Placement.student_id)))
        .where(Placement.drive_id.in_(drive_ids))
    ) or 0

    rate = round((total_placed / total_registered * 100), 2) if total_registered > 0 else 0.0

    stages = db.scalars(
        select(PlacementStage)
        .where(PlacementStage.drive_id.in_(drive_ids))
        .order_by(PlacementStage.stage_order.asc())
    ).all()

    stages_breakdown = []
    for s in stages:
        qualified_count = db.scalar(
            select(func.count(StudentStageResult.id))
            .where(StudentStageResult.stage_id == s.id, StudentStageResult.status == "QUALIFIED")
        ) or 0

        stages_breakdown.append({
            "stage_id": s.id,
            "stage_name": s.stage_name,
            "stage_order": s.stage_order,
            "category": s.normalized_category,
            "qualified_count": qualified_count
        })

    return {
        "company_id": company.id,
        "company_name": company.name,
        "total_drives": len(drives),
        "registered_candidates": total_registered,
        "placed_candidates": total_placed,
        "selection_rate_percentage": rate,
        "stages_breakdown": stages_breakdown
    }
