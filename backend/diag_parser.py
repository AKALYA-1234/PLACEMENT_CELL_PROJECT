"""Diagnostic: writes parser output to diag_out.txt"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app.services.excel_parser import parse_excel_workbook

files = {
    'netgear': os.path.join('..', 'sample_data', 'Netgear - Roundwise.xlsx'),
    'presidio': os.path.join('..', 'sample_data', 'PRESIDIO.xlsx'),
    'soliton': os.path.join('..', 'sample_data', 'Soliton Roundwise Details.xlsx'),
}

lines = []
for key, fp in files.items():
    wb = parse_excel_workbook(fp)
    lines.append(f"### {key.upper()} ###")
    lines.append(f"file_name={wb.file_name}")
    lines.append(f"total_sheets={wb.total_sheets}")
    lines.append(f"global_dupes={len(wb.global_duplicates)}")
    for i, s in enumerate(wb.parsed_sheets):
        lines.append(f"  [{i}] sheet={s.sheet_name!r}  cat={s.category.value}  hdr={s.header_row_index}  valid={s.valid_records_count}  total={s.total_rows}  empty={s.is_empty}  malformed={len(s.malformed_register_numbers)}  dupes={len(s.duplicate_register_numbers)}")
        if s.malformed_register_numbers:
            lines.append(f"      malformed_samples={s.malformed_register_numbers[:5]}")
        lines.append(f"      col_map={s.column_mapping}")
    lines.append("")

with open('diag_out.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("Written diag_out.txt")
