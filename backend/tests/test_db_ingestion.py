import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models import Student, Company, PlacementDrive, PlacementStage, StudentStageResult, Placement, ImportLog
from app.services.excel_parser import parse_excel_workbook, ingest_parsed_workbook

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data"))


def test_db_ingestion_presidio():
    file_path = os.path.join(SAMPLE_DIR, "PRESIDIO.xlsx")
    assert os.path.exists(file_path)

    parsed_wb = parse_excel_workbook(file_path)
    db = SessionLocal()
    try:
        log = ingest_parsed_workbook(
            db=db,
            parsed_wb=parsed_wb,
            company_name="Presidio Inc",
            academic_year="2025-2026"
        )
        assert log is not None
        assert log.status in ("SUCCESS", "PARTIAL_SUCCESS")

        company = db.scalar(select(Company).where(Company.name == "Presidio Inc"))
        assert company is not None

        drive = db.scalar(select(PlacementDrive).where(PlacementDrive.company_id == company.id))
        assert drive is not None

        # Check offer sheet placed count
        placed_count = db.scalar(
            select(func.count(Placement.id)).where(Placement.drive_id == drive.id)
        )
        assert placed_count == 3

    finally:
        db.close()


def test_db_ingestion_soliton():
    file_path = os.path.join(SAMPLE_DIR, "Soliton Roundwise Details.xlsx")
    assert os.path.exists(file_path)

    parsed_wb = parse_excel_workbook(file_path)
    db = SessionLocal()
    try:
        log = ingest_parsed_workbook(
            db=db,
            parsed_wb=parsed_wb,
            company_name="Soliton Technologies",
            academic_year="2025-2026"
        )
        assert log is not None

        company = db.scalar(select(Company).where(Company.name == "Soliton Technologies"))
        assert company is not None

        drive = db.scalar(select(PlacementDrive).where(PlacementDrive.company_id == company.id))
        assert drive is not None

        # Check OFFER sheet placed count
        placed_count = db.scalar(
            select(func.count(Placement.id)).where(Placement.drive_id == drive.id)
        )
        assert placed_count == 7

    finally:
        db.close()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
