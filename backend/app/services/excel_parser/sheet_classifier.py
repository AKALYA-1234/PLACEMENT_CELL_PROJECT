from typing import Any
from app.services.excel_parser.parser_models import SheetCategory

CATEGORY_KEYWORDS = {
    SheetCategory.PLACED: [
        "offer list", "offered list", "final selects", "final select",
        "final selection", "placed", "offer", "offered", "selects"
    ],
    SheetCategory.PROGRESSION: [
        "round", "shortlisted", "technical", "aptitude", "interview",
        "assessment", "ab", "test", "screening", "coding", "lab test",
        "design round", "selected"
    ],
    SheetCategory.REGISTERED: [
        "registration", "registered", "registration list", "master list",
        "applied", "eligible list", "sheet1"
    ],
    SheetCategory.IGNORE: [
        "sheet2", "sheet3", "sheet4", "instructions", "pivot", "template", "sample"
    ]
}


def classify_sheet(
    sheet_name: str,
    total_valid_records: int = 0,
    has_register_column: bool = True
) -> tuple[SheetCategory, float]:
    """
    Classifies a worksheet into REGISTERED, PROGRESSION, PLACED, UNKNOWN, or IGNORE.
    Returns:
        (SheetCategory, confidence_score)
    """
    name_clean = sheet_name.strip().lower()

    # Empty / Irrelevant sheet check
    if total_valid_records == 0 or not has_register_column:
        if any(kw in name_clean for kw in CATEGORY_KEYWORDS[SheetCategory.IGNORE]) or total_valid_records == 0:
            return SheetCategory.IGNORE, 1.0

    # 1. PLACED check (Highest precedence for definitive offer lists)
    if any(kw in name_clean for kw in ["offer", "final select", "final selection", "placed"]):
        return SheetCategory.PLACED, 0.95

    # 2. Ambiguous "selected" check:
    # If "selected" is accompanied by "round" or "screening" (e.g. "Selected - Round 2"), it is PROGRESSION
    if "selected" in name_clean:
        if any(kw in name_clean for kw in ["round", "screening", "test", "lab"]):
            return SheetCategory.PROGRESSION, 0.90
        # Otherwise, if standalone "selected" or "final", treat as PLACED or PROMPT FOR ADMIN CONFIRMATION
        return SheetCategory.PLACED, 0.75

    # 3. PROGRESSION check
    if any(kw in name_clean for kw in CATEGORY_KEYWORDS[SheetCategory.PROGRESSION]):
        return SheetCategory.PROGRESSION, 0.90

    # 4. REGISTERED check
    if any(kw in name_clean for kw in CATEGORY_KEYWORDS[SheetCategory.REGISTERED]):
        return SheetCategory.REGISTERED, 0.85

    # Default fallback based on record presence
    if total_valid_records > 0 and has_register_column:
        return SheetCategory.UNKNOWN, 0.50

    return SheetCategory.IGNORE, 0.90
