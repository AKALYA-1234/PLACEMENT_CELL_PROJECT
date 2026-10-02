from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.excel_parser.validation_models import ImportValidationResponse
from app.services.excel_parser.import_validation_service import validate_excel_import

router = APIRouter(prefix="/admin/import", tags=["Admin Import"])


@router.post("/validate", response_model=ImportValidationResponse)
async def validate_excel_import_endpoint(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    academic_year: str = Form("2025-2026"),
    db: Session = Depends(get_db)
) -> ImportValidationResponse:
    """
    Validates an uploaded Excel workbook for placement import without persisting changes to PostgreSQL.
    Returns a comprehensive validation preview report.
    """
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a valid Excel workbook (.xlsx or .xls)."
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    validation_response = validate_excel_import(
        file_input=contents,
        file_name=file.filename,
        company_name=company_name,
        academic_year=academic_year,
        db=db
    )

    return validation_response
