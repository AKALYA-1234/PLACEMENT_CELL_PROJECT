import psycopg2

HOST = "localhost"
PORT = 5432
USER = "openpg"
PASS = "openpgpwd"
DB_NAME = "placement_cell"

queries = {
    "Total Registered Students": """
        SELECT 
            COUNT(*) AS total_master_students
        FROM students;
    """,
    "Company Registrations Summary": """
        SELECT 
            c.name AS company_name,
            pd.drive_name,
            pd.academic_year,
            COUNT(sr.id) AS total_registrations
        FROM companies c
        JOIN placement_drives pd ON c.id = pd.company_id
        LEFT JOIN student_registrations sr ON pd.id = sr.drive_id
        GROUP BY c.id, c.name, pd.id, pd.drive_name, pd.academic_year
        ORDER BY total_registrations DESC;
    """,
    "Student Registered-Company Count": """
        SELECT 
            s.register_number,
            s.full_name,
            s.department,
            COUNT(DISTINCT pd.company_id) AS registered_company_count
        FROM students s
        JOIN student_registrations sr ON s.id = sr.student_id
        JOIN placement_drives pd ON sr.drive_id = pd.id
        GROUP BY s.id, s.register_number, s.full_name, s.department
        ORDER BY registered_company_count DESC, s.register_number ASC
        LIMIT 5;
    """,
    "Student Progression Count": """
        SELECT 
            s.register_number,
            s.full_name,
            pd.drive_name,
            COUNT(ssr.id) AS stages_cleared_count
        FROM students s
        JOIN student_stage_results ssr ON s.id = ssr.student_id
        JOIN placement_stages ps ON ssr.stage_id = ps.id
        JOIN placement_drives pd ON ps.drive_id = pd.id
        WHERE ssr.status = 'QUALIFIED'
        GROUP BY s.id, s.register_number, s.full_name, pd.id, pd.drive_name
        ORDER BY stages_cleared_count DESC
        LIMIT 5;
    """,
    "Student Placed Count": """
        SELECT 
            COUNT(DISTINCT student_id) AS total_unique_placed_students,
            COUNT(id) AS total_offers_issued,
            ROUND(AVG(package_ctc)::numeric, 2) AS overall_avg_ctc_lpa,
            MAX(package_ctc) AS highest_ctc_lpa
        FROM placements
        WHERE status IN ('OFFERED', 'ACCEPTED');
    """,
    "Company-Wise Placed Count": """
        SELECT 
            c.name AS company_name,
            pd.drive_name,
            COUNT(p.id) AS placed_student_count,
            ROUND(AVG(p.package_ctc)::numeric, 2) AS avg_package_lpa
        FROM companies c
        JOIN placement_drives pd ON c.id = pd.company_id
        JOIN placements p ON pd.id = p.drive_id
        WHERE p.status IN ('OFFERED', 'ACCEPTED')
        GROUP BY c.id, c.name, pd.id, pd.drive_name
        ORDER BY placed_student_count DESC;
    """,
    "Department-Wise Placement Statistics": """
        SELECT 
            s.department,
            COUNT(DISTINCT s.id) AS total_students,
            COUNT(DISTINCT p.student_id) AS placed_students,
            ROUND(
                (COUNT(DISTINCT p.student_id)::numeric / NULLIF(COUNT(DISTINCT s.id), 0)) * 100, 2
            ) AS placement_percentage,
            COALESCE(ROUND(AVG(p.package_ctc)::numeric, 2), 0.00) AS avg_package_lpa
        FROM students s
        LEFT JOIN placements p ON s.id = p.student_id AND p.status IN ('OFFERED', 'ACCEPTED')
        GROUP BY s.department
        ORDER BY placement_percentage DESC, placed_students DESC;
    """
}

def run_tests():
    conn = psycopg2.connect(host=HOST, port=PORT, user=USER, password=PASS, dbname=DB_NAME)
    cursor = conn.cursor()
    print("=== TESTING ANALYTICAL SQL QUERIES AGAINST POSTGRESQL ===\n")
    for title, sql in queries.items():
        print(f"--- {title} ---")
        cursor.execute(sql)
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        print(" | ".join(cols))
        for row in rows:
            print(" | ".join(str(val) for val in row))
        print()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_tests()
