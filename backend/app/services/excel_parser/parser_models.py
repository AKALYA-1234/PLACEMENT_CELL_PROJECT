from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class SheetCategory(str, Enum):
    REGISTERED = "REGISTERED"
    PROGRESSION = "PROGRESSION"
    PLACED = "PLACED"
    UNKNOWN = "UNKNOWN"
    IGNORE = "IGNORE"


class ParsedRecord(BaseModel):
    """Represents a single parsed student row in a sheet."""
    row_index: int
    register_number: str | None = None
    register_number_raw: str | None = None
    is_register_valid: bool = True
    student_name: str | None = None
    department: str | None = None
    status: str | None = "PRESENT"
    validation_errors: list[str] = Field(default_factory=list)
    raw_values: dict[str, Any] = Field(default_factory=dict)


class ParsedSheet(BaseModel):
    """Represents the complete parsed result for a single Excel worksheet."""
    sheet_name: str
    category: SheetCategory = SheetCategory.UNKNOWN
    confidence_score: float = 1.0
    header_row_index: int = 1
    column_mapping: dict[str, str] = Field(default_factory=dict)
    records: list[ParsedRecord] = Field(default_factory=list)
    total_rows: int = 0
    valid_records_count: int = 0
    duplicate_register_numbers: list[str] = Field(default_factory=list)
    malformed_register_numbers: list[str] = Field(default_factory=list)
    is_empty: bool = False
    warnings: list[str] = Field(default_factory=list)


class ParsedWorkbook(BaseModel):
    """Represents the complete parsed result for an entire Excel workbook."""
    file_name: str
    file_path: str | None = None
    total_sheets: int = 0
    parsed_sheets: list[ParsedSheet] = Field(default_factory=list)
    global_student_count: int = 0
    global_duplicates: list[str] = Field(default_factory=list)
    anomalies_summary: dict[str, Any] = Field(default_factory=dict)
