import os
import re
from typing import Any, Optional
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.config import get_settings
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models import ImportLog, Company, PlacementDrive
from app.utils.security import get_current_admin
from app.services.excel_parser.validation_models import ImportValidationResponse
from app.services.excel_parser.confirm_models import ImportConfirmResponse
from app.services.excel_parser.import_validation_service import validate_excel_import
from app.services.excel_parser.import_confirm_service import confirm_excel_import

router = APIRouter(prefix="/admin/import", tags=["Admin Import"])
settings = get_settings()


def sanitize_filename(filename: str) -> str:
    """Sanitizes uploaded filename to prevent directory traversal or invalid characters."""
    clean_name = os.path.basename(filename)
    clean_name = re.sub(r"[^\w\s\.-]", "_", clean_name)
    return clean_name or "uploaded_workbook.xlsx"


@router.post("/validate", response_model=ImportValidationResponse)
async def validate_excel_import_endpoint(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    academic_year: str = Form("2025-2026"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> ImportValidationResponse:
    """Validates an uploaded Excel workbook for placement import without persisting changes to PostgreSQL."""
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a valid Excel workbook (.xlsx or .xls)."
        )

    safe_filename = sanitize_filename(file.filename)
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if len(contents) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum allowed size limit of {settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024):.0f} MB."
        )

    return validate_excel_import(
        file_input=contents,
        file_name=safe_filename,
        company_name=company_name,
        academic_year=academic_year,
        db=db
    )


@router.post("/confirm", response_model=ImportConfirmResponse)
async def confirm_excel_import_endpoint(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    academic_year: str = Form("2025-2026"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> ImportConfirmResponse:
    """Confirms and executes PostgreSQL database insertion for a validated Excel workbook."""
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a valid Excel workbook (.xlsx or .xls)."
        )

    safe_filename = sanitize_filename(file.filename)
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if len(contents) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum allowed size limit of {settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024):.0f} MB."
        )

    try:
        return confirm_excel_import(
            file_input=contents,
            file_name=safe_filename,
            company_name=company_name,
            academic_year=academic_year,
            db=db
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed during database execution: {str(e)}"
        )


@router.get("s")
async def list_imports_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by filename or company name"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by import status"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves paginated historical import logs."""
    query = select(ImportLog, Company.name.label("company_name"))\
        .outerjoin(Company, ImportLog.company_id == Company.id)

    if search:
        query = query.where(
            or_(
                ImportLog.filename.ilike(f"%{search}%"),
                Company.name.ilike(f"%{search}%")
            )
        )
    if status_filter:
        query = query.where(ImportLog.status == status_filter.upper())

    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    offset = (page - 1) * limit
    query = query.order_by(ImportLog.imported_at.desc()).offset(offset).limit(limit)
    results = db.execute(query).all()

    items = []
    for log, comp_name in results:
        items.append({
            "id": log.id,
            "filename": log.filename,
            "file_type": log.file_type,
            "company_id": log.company_id,
            "company_name": comp_name or "N/A",
            "drive_id": log.drive_id,
            "total_rows": log.total_rows,
            "imported_rows": log.imported_rows,
            "failed_rows": log.failed_rows,
            "status": log.status,
            "imported_at": log.imported_at.isoformat() if log.imported_at else None
        })

    pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


@router.get("s/{import_id}")
async def get_import_detail_endpoint(
    import_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Retrieves detailed record for a specific import log."""
    log = db.scalar(select(ImportLog).where(ImportLog.id == import_id))
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Import log with ID {import_id} not found."
        )

    company_name = "N/A"
    if log.company_id:
        comp = db.scalar(select(Company.name).where(Company.id == log.company_id))
        if comp:
            company_name = comp

    drive_name = "N/A"
    if log.drive_id:
        d_name = db.scalar(select(PlacementDrive.drive_name).where(PlacementDrive.id == log.drive_id))
        if d_name:
            drive_name = d_name

    return {
        "id": log.id,
        "filename": log.filename,
        "file_type": log.file_type,
        "company_id": log.company_id,
        "company_name": company_name,
        "drive_id": log.drive_id,
        "drive_name": drive_name,
        "total_rows": log.total_rows,
        "imported_rows": log.imported_rows,
        "failed_rows": log.failed_rows,
        "status": log.status,
        "error_details": log.error_details,
        "imported_at": log.imported_at.isoformat() if log.imported_at else None
    }
