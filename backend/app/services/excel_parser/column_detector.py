import re
from typing import Any

COLUMN_ALIASES = {
    "register_number": [
        "reg no.", "reg no", "roll number", "roll / reg no", "roll/reg no",
        "register number", "reg number", "roll no", "reg.no", "reg. no",
        "roll / reg", "roll/reg", "register no", "student reg no"
    ],
    "student_name": [
        "name", "student name", "candidates name", "full name",
        "candidate name", "name of candidate", "student_name", "name of the student"
    ],
    "department": [
        "department", "dept", "branch", "specialization", "sec", "section", "dept name"
    ],
    "status": [
        "status", "result", "round status", "remarks", "remark", "selection status"
    ]
}

REGISTER_PATTERN = re.compile(r"^7376\d{2}[A-Za-z0-9]{5,6}$", re.IGNORECASE)


def detect_column_mappings(headers: list[str], sample_data_rows: list[list[Any]] | None = None) -> dict[str, str]:
    """
    Detects which header column corresponds to register_number, student_name, department, and status.
    Returns:
        {"register_number": "Reg No.", "student_name": "Name", "department": "Department", ...}
    """
    mapping: dict[str, str] = {}

    headers_clean = [str(h).strip() for h in headers if h is not None]

    # Step 1: Match by exact or fuzzy alias keywords
    for field, aliases in COLUMN_ALIASES.items():
        if field in mapping:
            continue

        for header in headers_clean:
            h_lower = header.lower().strip()
            # Direct match or exact alias match
            if any(alias == h_lower or (len(alias) > 3 and alias in h_lower) for alias in aliases):
                mapping[field] = header
                break

    # Step 2: Data-driven fallback for register_number (e.g. Soliton S.No containing register numbers)
    if "register_number" not in mapping and sample_data_rows:
        for col_idx, header in enumerate(headers_clean):
            # Check sample rows for this column
            reg_matches = 0
            total_samples = 0
            for row in sample_data_rows[:15]:
                if col_idx < len(row) and row[col_idx] is not None:
                    cell_val = re.sub(r"\s+", "", str(row[col_idx])).upper()
                    if cell_val:
                        total_samples += 1
                        if REGISTER_PATTERN.match(cell_val):
                            reg_matches += 1

            if total_samples > 0 and (reg_matches / total_samples) >= 0.5:
                mapping["register_number"] = header
                break

    return mapping
