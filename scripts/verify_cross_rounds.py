import json
import os

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data")

with open(os.path.join(SAMPLE_DIR, "deep_analysis.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

out_file = os.path.join(SAMPLE_DIR, "cross_round_report.txt")
with open(out_file, "w", encoding="utf-8") as out:
    out.write("==========================================\n")
    out.write("CROSS-ROUND PROGRESSION & ANOMALY REPORT\n")
    out.write("==========================================\n")

    for fname, fcontent in data.items():
        out.write(f"\nWORKBOOK: {fname}\n")
        sheets = fcontent["sheets"]
        snames = list(sheets.keys())
        
        # Master list of all registered students in workbook (first sheet usually)
        master_regs = set(sheets[snames[0]]["reg_numbers_list"])
        
        for i in range(len(snames)):
            sname = snames[i]
            s_info = sheets[sname]
            regs = set(s_info["reg_numbers_list"])
            out.write(f"\n  Sheet [{sname}]: {s_info['record_count']} records, {s_info['unique_reg_count']} unique reg numbers\n")
            out.write(f"    Header Row: {s_info['header_row_1based']}, Reg Header: '{s_info['reg_col_header']}', Name Header: '{s_info['name_col_header']}', Dept Header: '{s_info['dept_col_header']}'\n")
            
            if s_info["malformed_regs"]:
                out.write(f"    ⚠️ Malformed Reg Nos ({len(s_info['malformed_regs'])}): {s_info['malformed_regs']}\n")
            if s_info["duplicate_regs"]:
                out.write(f"    ⚠️ Duplicate Reg Nos ({len(s_info['duplicate_regs'])}): {s_info['duplicate_regs']}\n")
                
            # Compare with master sheet
            if i > 0:
                missing_in_master = regs - master_regs
                if missing_in_master and sname != "AB":
                    out.write(f"    ⚠️ WARNING: {len(missing_in_master)} reg number(s) in '{sname}' were NOT present in initial sheet '{snames[0]}': {list(missing_in_master)}\n")
                else:
                    out.write(f"    ✅ All {len(regs)} reg numbers in '{sname}' exist in initial sheet '{snames[0]}'\n")

if __name__ == "__main__":
    print(f"Report written to {out_file}")
