from typing import Any
from pydantic import BaseModel, Field


class ImportConfirmResponse(BaseModel):
    """Response returned upon successful confirmed ingestion into PostgreSQL."""
    status: str = "SUCCESS"
    message: str
    import_log_id: int
    company_id: int
    drive_id: int
    company_name: str
    drive_name: str
    academic_year: str
    total_records_processed: int
    imported_records_count: int
    failed_records_count: int
    statistics: dict[str, Any] = Field(default_factory=dict)
