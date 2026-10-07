import os
import re
import glob
import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.excel_parser.import_confirm_service import confirm_excel_import

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAMPLE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_data"))

def clean_company_name(filename: str) -> str:
    name = os.path.splitext(filename)[0]
    # Remove year patterns like 2023-2027, 2027 BATCH, etc.
    name = re.sub(r'20\d{2}\s*[-_–]?\s*20\d{2}', '', name, flags=re.IGNORECASE)
    name = re.sub(r'20\d{2}\s*batch', '', name, flags=re.IGNORECASE)
    name = re.sub(r'20\d{2}', '', name, flags=re.IGNORECASE)
    name = re.sub(r'batch\s*\d*', '', name, flags=re.IGNORECASE)
    # Remove common words like Roundwise, Details, Data, List, Technical
    name = re.sub(r'Round\s*wise', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Details', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Data', '', name, flags=re.IGNORECASE)
    name = re.sub(r'List', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Technical', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Declaration form not submitted students', '', name, flags=re.IGNORECASE)
    # Clean up underscores, dashes, multiple spaces
    name = name.replace('__', ' ').replace('_', ' ').replace('-', ' ').strip()
    name = re.sub(r'\s+', ' ', name)
    return name or os.path.splitext(filename)[0]

def batch_import():
    db: Session = SessionLocal()
    try:
        excel_files = glob.glob(os.path.join(SAMPLE_DATA_DIR, "*.xlsx")) + glob.glob(os.path.join(SAMPLE_DATA_DIR, "*.xls"))
        logger.info("Found %d Excel files to process in %s", len(excel_files), SAMPLE_DATA_DIR)

        success_count = 0
        skipped_count = 0
        failed_count = 0

        for file_path in excel_files:
            filename = os.path.basename(file_path)
            company_name = clean_company_name(filename)
            academic_year = "2025-2026"
            if "2027" in filename or "2023-2027" in filename:
                academic_year = "2026-2027"
            elif "2024" in filename or "2025" in filename:
                academic_year = "2024-2025"

            logger.info("Importing file '%s' -> Company: '%s', Year: '%s'...", filename, company_name, academic_year)
            try:
                res = confirm_excel_import(
                    file_input=file_path,
                    file_name=filename,
                    company_name=company_name,
                    academic_year=academic_year,
                    db=db
                )
                logger.info("SUCCESS: %s (Processed: %d, Imported: %d)", filename, res.total_records_processed, res.imported_records_count)
                success_count += 1
            except Exception as e:
                logger.error("FAILED to import '%s': %s", filename, e)
                failed_count += 1
                db.rollback()

        logger.info("\nBatch Import Complete!\nSuccess: %d, Failed: %d, Total Files: %d", success_count, failed_count, len(excel_files))
    finally:
        db.close()

if __name__ == "__main__":
    batch_import()
