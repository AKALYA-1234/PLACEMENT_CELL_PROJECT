import os
import glob
import re
import json
import openpyxl
import pandas as pd

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data")

REG_NO_KEYWORDS = ["reg", "roll", "htno", "register", "registration", "student id", "arn", "enrollment"]
NAME_KEYWORDS = ["name", "student name", "candidate", "full name"]
DEPT_KEYWORDS = ["dept", "department", "branch", "stream", "degree", "course", "sec", "section"]
STATUS_KEYWORDS = ["status", "round", "selected", "offered", "result", "shortlist", "remarks", "placed"]
CGPA_KEYWORDS = ["cgpa", "gpa", "percentage", "%", "marks", "score"]
GENDER_KEYWORDS = ["gender", "sex"]

def is_reg_no_header(cell_val):
    if not cell_val:
        return False
    val = str(cell_val).lower().strip()
    return any(k in val for k in REG_NO_KEYWORDS)

def is_name_header(cell_val):
    if not cell_val:
        return False
    val = str(cell_val).lower().strip()
    return any(k in val for k in NAME_KEYWORDS) and not is_reg_no_header(cell_val)

def is_dept_header(cell_val):
    if not cell_val:
        return False
    val = str(cell_val).lower().strip()
    return any(k in val for k in DEPT_KEYWORDS)

def analyze_workbook(file_path):
    filename = os.path.basename(file_path)
    wb = openpyxl.load_workbook(file_path, data_only=True)
    
    workbook_report = {
        "file_name": filename,
        "file_size_bytes": os.path.getsize(file_path),
        "sheet_names": wb.sheetnames,
        "sheets_analysis": []
    }

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        max_row = ws.max_row
        max_col = ws.max_column
        
        # Read top rows to find header
        rows_data = []
        for r in range(1, min(max_row + 1, 50)):
            row_vals = [ws.cell(row=r, column=c).value for c in range(1, min(max_col + 1, 30))]
            rows_data.append((r, row_vals))
            
        header_row_idx = None
        best_header_score = 0
        detected_headers = []
        
        for r_idx, r_vals in rows_data:
            score = 0
            headers_in_row = []
            non_empty_str_count = 0
            for val in r_vals:
                if val is not None and str(val).strip():
                    sval = str(val).strip()
                    non_empty_str_count += 1
                    headers_in_row.append(sval)
                    sval_lower = sval.lower()
                    if any(k in sval_lower for k in REG_NO_KEYWORDS):
                        score += 5
                    if any(k in sval_lower for k in NAME_KEYWORDS):
                        score += 3
                    if any(k in sval_lower for k in DEPT_KEYWORDS):
                        score += 2
                    if any(k in sval_lower for k in STATUS_KEYWORDS):
                        score += 2
                    if any(k in sval_lower for k in CGPA_KEYWORDS):
                        score += 1
            if score > best_header_score or (score == best_header_score and score > 0 and non_empty_str_count > len(detected_headers)):
                best_header_score = score
                header_row_idx = r_idx
                detected_headers = headers_in_row
                
        # Analyze data columns based on header
        col_mappings = {}
        header_list = []
        if header_row_idx:
            for c in range(1, min(max_col + 1, 40)):
                c_val = ws.cell(row=header_row_idx, column=c).value
                c_str = str(c_val).strip() if c_val is not None else f"Column_{c}"
                header_list.append(c_str)
                c_lower = c_str.lower()
                
                if not col_mappings.get("reg_no") and any(k in c_lower for k in REG_NO_KEYWORDS):
                    col_mappings["reg_no"] = (c, c_str)
                elif not col_mappings.get("name") and is_name_header(c_str):
                    col_mappings["name"] = (c, c_str)
                elif not col_mappings.get("dept") and is_dept_header(c_str):
                    col_mappings["dept"] = (c, c_str)
                elif any(k in c_lower for k in GENDER_KEYWORDS) and not col_mappings.get("gender"):
                    col_mappings["gender"] = (c, c_str)
                elif any(k in c_lower for k in CGPA_KEYWORDS) and not col_mappings.get("cgpa"):
                    col_mappings["cgpa"] = (c, c_str)
                elif any(k in c_lower for k in STATUS_KEYWORDS):
                    if "status_cols" not in col_mappings:
                        col_mappings["status_cols"] = []
                    col_mappings["status_cols"].append((c, c_str))

        # Iterate data rows
        records_count = 0
        reg_numbers = []
        duplicate_reg_nos = []
        malformed_reg_nos = []
        seen_reg_nos = set()
        dept_counts = {}
        sample_records = []
        
        start_row = (header_row_idx + 1) if header_row_idx else 1
        
        for r in range(start_row, max_row + 1):
            row_cells = [ws.cell(row=r, column=c).value for c in range(1, min(max_col + 1, 40))]
            if not any(v is not None and str(v).strip() for v in row_cells):
                continue # Skip empty row
                
            reg_val = None
            name_val = None
            dept_val = None
            
            if col_mappings.get("reg_no"):
                c_idx = col_mappings["reg_no"][0]
                reg_val = ws.cell(row=r, column=c_idx).value
            if col_mappings.get("name"):
                c_idx = col_mappings["name"][0]
                name_val = ws.cell(row=r, column=c_idx).value
            if col_mappings.get("dept"):
                c_idx = col_mappings["dept"][0]
                dept_val = ws.cell(row=r, column=c_idx).value
                
            # If no reg_no column identified, try to find a cell matching register number pattern
            if reg_val is None:
                for val in row_cells:
                    if val is not None:
                        s = str(val).strip()
                        # pattern match 7-15 alphanumeric chars with digits
                        if re.match(r'^[A-Za-z0-9]{6,15}$', s) and any(char.isdigit() for char in s) and not s.isdigit():
                            reg_val = s
                            break

            if reg_val is not None or name_val is not None or any(v is not None and str(v).strip() for v in row_cells):
                records_count += 1
                
            if reg_val is not None:
                reg_str = str(reg_val).strip()
                # Remove scientific notation if formatted as float like 7.37621E+11
                if isinstance(reg_val, float):
                    reg_str = f"{int(reg_val)}"
                reg_numbers.append(reg_str)
                
                if reg_str in seen_reg_nos:
                    duplicate_reg_nos.append((r, reg_str))
                else:
                    seen_reg_nos.add(reg_str)
                    
                # Malformed check: length < 5, spaces, special chars, header text repeated, etc.
                if len(reg_str) < 5 or len(reg_str) > 20 or re.search(r'[\s!@#$%^&*()=+[\]{};:",<>?|\\]', reg_str) or any(k in reg_str.lower() for k in REG_NO_KEYWORDS):
                    malformed_reg_nos.append((r, reg_str))
                    
            if dept_val is not None:
                d_str = str(dept_val).strip()
                dept_counts[d_str] = dept_counts.get(d_str, 0) + 1
                
            if len(sample_records) < 3 and (reg_val or name_val):
                sample_records.append({
                    "row": r,
                    "reg_no": str(reg_val) if reg_val else None,
                    "name": str(name_val) if name_val else None,
                    "dept": str(dept_val) if dept_val else None
                })
                
        # Categorize sheet type
        sheet_category = "Ambiguous / Other"
        lower_sheet = sheet_name.lower()
        if records_count == 0 or (header_row_idx is None and len(header_list) < 2):
            sheet_category = "Empty / Irrelevant"
        elif "select" in lower_sheet or "offer" in lower_sheet or "placed" in lower_sheet or "final" in lower_sheet:
            sheet_category = "Placed / Offered Sheet"
        elif "round" in lower_sheet or "shortlist" in lower_sheet or "level" in lower_sheet or "test" in lower_sheet:
            sheet_category = "Progression Sheet"
        elif "register" in lower_sheet or "applicant" in lower_sheet or "all" in lower_sheet or "database" in lower_sheet or "eligible" in lower_sheet:
            sheet_category = "Registered Sheet"
        elif col_mappings.get("reg_no") and col_mappings.get("name"):
            if any("round" in str(c).lower() or "status" in str(c).lower() or "result" in str(c).lower() for c in header_list):
                sheet_category = "Progression Sheet"
            else:
                sheet_category = "Registered / Master Sheet"

        sheet_report = {
            "sheet_name": sheet_name,
            "max_row": max_row,
            "max_column": max_col,
            "header_row_idx": header_row_idx,
            "headers": header_list,
            "mapped_columns": {k: (v[0], v[1]) if isinstance(v, tuple) else v for k, v in col_mappings.items()},
            "records_count": records_count,
            "unique_reg_nos_count": len(seen_reg_nos),
            "duplicate_reg_nos_count": len(duplicate_reg_nos),
            "duplicate_samples": duplicate_reg_nos[:5],
            "malformed_reg_nos_count": len(malformed_reg_nos),
            "malformed_samples": malformed_reg_nos[:5],
            "sheet_category": sheet_category,
            "sample_records": sample_records,
            "department_breakdown": dept_counts
        }
        
        workbook_report["sheets_analysis"].append(sheet_report)
        
    return workbook_report

def main():
    excel_files = glob.glob(os.path.join(SAMPLE_DIR, "*.xlsx")) + glob.glob(os.path.join(SAMPLE_DIR, "*.xls"))
    print(f"Found {len(excel_files)} Excel file(s) in {SAMPLE_DIR}")
    
    all_reports = []
    for f in excel_files:
        print(f"\n==========================================")
        print(f"Analyzing Workbook: {os.path.basename(f)}")
        print(f"==========================================")
        report = analyze_workbook(f)
        all_reports.append(report)
        
        # Print summary for this workbook
        print(f"Sheets ({len(report['sheet_names'])}): {', '.join(report['sheet_names'])}")
        for s in report["sheets_analysis"]:
            print(f"\n  --- Sheet: '{s['sheet_name']}' ---")
            print(f"  Category: {s['sheet_category']}")
            print(f"  Dimensions: {s['max_row']} rows x {s['max_column']} cols")
            print(f"  Header Row: {s['header_row_idx']}")
            print(f"  Headers: {s['headers']}")
            print(f"  Mapped Columns: {s['mapped_columns']}")
            print(f"  Record Count: {s['records_count']}")
            print(f"  Unique Reg Nos: {s['unique_reg_nos_count']}")
            print(f"  Duplicates Count: {s['duplicate_reg_nos_count']}")
            if s['duplicate_samples']:
                print(f"    Sample Duplicates: {s['duplicate_samples']}")
            print(f"  Malformed Reg Nos Count: {s['malformed_reg_nos_count']}")
            if s['malformed_samples']:
                print(f"    Sample Malformed: {s['malformed_samples']}")
            if s['department_breakdown']:
                print(f"  Departments: {dict(list(s['department_breakdown'].items())[:5])}")

    # Output detailed report JSON
    report_json_path = os.path.join(SAMPLE_DIR, "analysis_results.json")
    with open(report_json_path, "w", encoding="utf-8") as out:
        json.dump(all_reports, out, indent=2)
    print(f"\nFull analysis exported to {report_json_path}")

if __name__ == "__main__":
    main()
