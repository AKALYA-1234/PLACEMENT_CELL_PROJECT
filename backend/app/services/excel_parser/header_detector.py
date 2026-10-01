from typing import Any
import re

HEADER_KEYWORDS = {
    "register_number": ["reg", "roll", "register", "roll / reg", "roll/reg", "reg no", "roll no", "reg number", "roll number"],
    "student_name": ["name", "student name", "candidates name", "full name", "candidate name"],
    "department": ["dept", "department", "branch", "specialization", "sec", "section"],
    "status": ["status", "result", "remark", "remarks", "round status", "selection"]
}


def detect_header_row(rows: list[list[Any]], max_scan_rows: int = 10) -> tuple[int, list[str]]:
    """
    Scans the top N rows of a sheet to locate the header row.
    Returns:
        (header_row_1indexed, header_strings)
    """
    best_row_idx = 0  # 0-indexed
    best_score = -1
    best_headers: list[str] = []

    for row_idx in range(min(max_scan_rows, len(rows))):
        row = rows[row_idx]
        if not row or all(cell is None or str(cell).strip() == "" for cell in row):
            continue

        score = 0
        row_str_lower = [str(cell).strip().lower() if cell is not None else "" for cell in row]

        # Check for presence of key header concepts
        has_reg = any(any(kw in cell for kw in HEADER_KEYWORDS["register_number"]) for cell in row_str_lower)
        has_name = any(any(kw in cell for kw in HEADER_KEYWORDS["student_name"]) for cell in row_str_lower)
        has_dept = any(any(kw in cell for kw in HEADER_KEYWORDS["department"]) for cell in row_str_lower)

        if has_reg:
            score += 10
        if has_name:
            score += 8
        if has_dept:
            score += 5

        # Penalize title banners (very long strings in single cell)
        non_empty_cells = [c for c in row_str_lower if c]
        if len(non_empty_cells) == 1 and len(non_empty_cells[0]) > 30:
            score -= 15

        if score > best_score:
            best_score = score
            best_row_idx = row_idx
            best_headers = [str(cell).strip() if cell is not None else f"Column_{i+1}" for i, cell in enumerate(row)]

    # Fallback to row 1 if no headers identified with positive score
    if best_score <= 0 and rows:
        best_row_idx = 0
        best_headers = [str(cell).strip() if cell is not None else f"Column_{i+1}" for i, cell in enumerate(rows[0])]

    return best_row_idx + 1, best_headers
