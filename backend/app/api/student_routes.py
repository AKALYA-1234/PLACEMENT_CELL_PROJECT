from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, desc, asc, nulls_last

from app.database import get_db
from app.models.admin_user import AdminUser
from app.models import Student, StudentRegistration, StudentStageResult, Placement, PlacementDrive, Company, PlacementStage
from app.utils.security import get_current_admin

router = APIRouter(prefix="/admin/students", tags=["Admin Students"])


DEPARTMENT_MAPPINGS: dict[str, list[str]] = {
    "IT": ["Information Technology", "Information Science", "IT"],
    "CSE": ["Computer Science", "CSE"],
    "ECE": ["Electronics and Communication", "ECE"],
    "EEE": ["Electrical and Electronics", "EEE"],
    "MECH": ["Mechanical Engineering", "MECH"],
    "CIVIL": ["Civil Engineering", "CIVIL"],
    "AIDS": ["Artificial Intelligence", "AIDS"],
    "AIML": ["Machine Learning", "AIML"],
    "BM": ["Biomedical", "BM"],
    "BME": ["Biomedical", "BME"]
}

@router.get("/departments")
async def list_student_departments_endpoint(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves all distinct department names present in the student database."""
    depts = db.scalars(
        select(Student.department).where(Student.department.is_not(None)).distinct()
    ).all()
    clean_depts = sorted([d for d in depts if d and d.strip()])
    return {"departments": clean_depts}


@router.get("")
async def list_students_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by register number or student name"),
    department: Optional[str] = Query(None, description="Filter by department name"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    placed_status: Optional[str] = Query(None, alias="status", description="Filter by placement status (PLACED / UNPLACED)"),
    sort_by: str = Query("register_number", description="Field to sort by: register_number, full_name, cgpa, department"),
    order: str = Query("asc", description="Sort order: asc or desc"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves a paginated list of students with search, filtering, and sorting capabilities."""
    query = select(Student)

    if search:
        query = query.where(
            or_(
                Student.register_number.ilike(f"%{search}%"),
                Student.full_name.ilike(f"%{search}%")
            )
        )

    if department and department.strip():
        dept_str = department.strip()
        dept_upper = dept_str.upper()
        if dept_upper in DEPARTMENT_MAPPINGS:
            matched_terms = DEPARTMENT_MAPPINGS[dept_upper]
            conditions = [Student.department.ilike(f"%{term}%") for term in matched_terms]
            query = query.where(or_(*conditions))
        else:
            query = query.where(Student.department.ilike(f"%{dept_str}%"))

    if academic_year:
        query = query.where(Student.academic_year == academic_year)

    if placed_status:
        placed_subq = select(Placement.student_id).scalar_subquery()
        if placed_status.upper() == "PLACED":
            query = query.where(Student.id.in_(placed_subq))
        elif placed_status.upper() == "UNPLACED":
            query = query.where(~Student.id.in_(placed_subq))

    # Total count query
    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    # Sorting
    sort_columns = {
        "register_number": Student.register_number,
        "full_name": Student.full_name,
        "cgpa": Student.cgpa,
        "department": Student.department,
    }
    sort_col = sort_columns.get(sort_by, Student.register_number)
    if order.lower() == "desc":
        query = query.order_by(nulls_last(desc(sort_col)), desc(Student.register_number))
    else:
        query = query.order_by(nulls_last(asc(sort_col)), asc(Student.register_number))

    # Pagination
    offset = (page - 1) * limit
    students = db.scalars(query.offset(offset).limit(limit)).all()

    # Pre-fetch placement status mapping for retrieved students
    student_ids = [s.id for s in students]
    placements_map: dict[int, list[dict[str, Any]]] = {}
    if student_ids:
        pl_rows = db.execute(
            select(Placement, Company.name.label("company_name"), PlacementDrive.drive_name)
            .join(PlacementDrive, Placement.drive_id == PlacementDrive.id)
            .join(Company, PlacementDrive.company_id == Company.id)
            .where(Placement.student_id.in_(student_ids))
        ).all()

        for pl, comp_name, drive_n in pl_rows:
            if pl.student_id not in placements_map:
                placements_map[pl.student_id] = []
            placements_map[pl.student_id].append({
                "company_name": comp_name,
                "drive_name": drive_n,
                "status": pl.status,
                "package_ctc": pl.package_ctc
            })

    items = []
    for s in students:
        p_list = placements_map.get(s.id, [])
        is_placed = len(p_list) > 0
        items.append({
            "id": s.id,
            "register_number": s.register_number,
            "full_name": s.full_name,
            "department": s.department,
            "email": s.email,
            "mobile_number": s.mobile_number,
            "cgpa": s.cgpa,
            "academic_year": s.academic_year,
            "is_placed": is_placed,
            "placement_count": len(p_list),
            "placements": p_list
        })

    pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


@router.get("/{register_number}")
async def get_student_detail_endpoint(
    register_number: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves full profile details of a student by register number including drive participations and stage results."""
    student = db.scalar(select(Student).where(Student.register_number.ilike(register_number)))
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with register number '{register_number}' not found."
        )

    # Participated Drives & Stage Results
    reg_rows = db.execute(
        select(StudentRegistration, PlacementDrive, Company)
        .join(PlacementDrive, StudentRegistration.drive_id == PlacementDrive.id)
        .join(Company, PlacementDrive.company_id == Company.id)
        .where(StudentRegistration.student_id == student.id)
    ).all()

    drives_history = []
    for reg, drive, company in reg_rows:
        # Fetch Stage Results for this drive registration
        stage_res_rows = db.execute(
            select(StudentStageResult, PlacementStage)
            .join(PlacementStage, StudentStageResult.stage_id == PlacementStage.id)
            .where(StudentStageResult.registration_id == reg.id)
            .order_by(PlacementStage.stage_order.asc())
        ).all()

        stage_results = [
            {
                "stage_name": stage.stage_name,
                "stage_order": stage.stage_order,
                "status": sr.status
            }
            for sr, stage in stage_res_rows
        ]

        # Fetch placement offer if any
        placement = db.scalar(
            select(Placement).where(
                Placement.student_id == student.id,
                Placement.drive_id == drive.id
            )
        )

        drives_history.append({
            "drive_id": drive.id,
            "drive_name": drive.drive_name,
            "company_id": company.id,
            "company_name": company.name,
            "academic_year": drive.academic_year,
            "stage_results": stage_results,
            "placement": {
                "status": placement.status,
                "package_ctc": placement.package_ctc
            } if placement else None
        })

    return {
        "id": student.id,
        "register_number": student.register_number,
        "full_name": student.full_name,
        "department": student.department,
        "email": student.email,
        "mobile_number": student.mobile_number,
        "gender": student.gender,
        "accommodation_type": student.accommodation_type,
        "cgpa": student.cgpa,
        "academic_year": student.academic_year,
        "is_placed": any(d["placement"] is not None for d in drives_history),
        "drives_history": drives_history
    }
