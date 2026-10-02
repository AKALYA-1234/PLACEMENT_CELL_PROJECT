from typing import Any
from pydantic import BaseModel, Field
from app.services.excel_parser.parser_models import SheetCategory


class SheetValidationSummary(BaseModel):
    """Summary metrics for a single detected worksheet."""
    sheet_name: str
    category: SheetCategory
    header_row_index: int
    total_records: int
    valid_records_count: int
    malformed_count: int
    duplicate_count: int
    column_mapping: dict[str, str] = Field(default_factory=dict)
    sample_records: list[dict[str, Any]] = Field(default_factory=list)


class ValidationConflict(BaseModel):
    """Represents a potential conflict or anomaly flagged during preview validation."""
    severity: str  # "WARNING", "ERROR", "INFO"
    conflict_type: str  # "MISSING_STUDENT", "DUPLICATE_REGISTER", "MALFORMED_REGISTER", "STATUS_MISMATCH"
    sheet_name: str | None = None
    row_index: int | None = None
    register_number: str | None = None
    message: str


class ImportValidationResponse(BaseModel):
    """Structured, non-mutating preview response returned by POST /admin/import/validate."""
    company_name: str
    academic_year: str
    file_name: str
    total_sheets: int
    detected_sheets: list[SheetValidationSummary] = Field(default_factory=list)
    
    # Aggregated record counts
    total_records_count: int = 0
    registered_count: int = 0
    progression_count: int = 0
    placed_count: int = 0
    unknown_sheets_count: int = 0
    
    # Anomaly lists
    missing_register_numbers: list[dict[str, Any]] = Field(default_factory=list)
    invalid_register_numbers: list[dict[str, Any]] = Field(default_factory=list)
    duplicate_register_numbers: list[str] = Field(default_factory=list)
    students_not_found_in_master: list[str] = Field(default_factory=list)
    
    # Detailed conflicts list
    possible_conflicts: list[ValidationConflict] = Field(default_factory=list)
    is_valid_for_import: bool = True
