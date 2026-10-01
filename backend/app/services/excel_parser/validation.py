from collections import Counter
from typing import Any
from app.services.excel_parser.parser_models import ParsedRecord, ParsedSheet


def find_sheet_anomalies(records: list[ParsedRecord]) -> tuple[list[str], list[str]]:
    """
    Scans parsed records within a single sheet for duplicate and malformed register numbers.
    Returns:
        (duplicate_registers, malformed_registers)
    """
    valid_regs: list[str] = []
    malformed_regs: list[str] = []

    for r in records:
        if r.register_number:
            if r.is_register_valid:
                valid_regs.append(r.register_number)
            else:
                malformed_regs.append(r.register_number)

    # Find duplicates
    counts = Counter(valid_regs)
    duplicates = [reg for reg, count in counts.items() if count > 1]

    return sorted(duplicates), sorted(set(malformed_regs))


def summarize_workbook_anomalies(sheets: list[ParsedSheet]) -> dict[str, Any]:
    """
    Aggregates global duplicate register numbers and anomaly stats across all sheets in a workbook.
    """
    global_register_sheet_map: dict[str, list[str]] = {}
    total_valid_records = 0
    total_malformed_records = 0

    for sheet in sheets:
        if sheet.is_empty or sheet.category == "IGNORE":
            continue

        for r in sheet.records:
            if r.register_number and r.is_register_valid:
                total_valid_records += 1
                if r.register_number not in global_register_sheet_map:
                    global_register_sheet_map[r.register_number] = []
                global_register_sheet_map[r.register_number].append(sheet.sheet_name)
            elif r.register_number and not r.is_register_valid:
                total_malformed_records += 1

    # Cross-sheet duplicates
    global_duplicates = [
        reg for reg, sheet_list in global_register_sheet_map.items() if len(sheet_list) > 1
    ]

    return {
        "total_valid_records": total_valid_records,
        "total_malformed_records": total_malformed_records,
        "global_duplicates_count": len(global_duplicates),
        "global_duplicates": sorted(global_duplicates)
    }
