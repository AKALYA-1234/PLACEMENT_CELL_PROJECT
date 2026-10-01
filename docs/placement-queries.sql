-- =============================================================================
-- PLACEMENT CELL PORTAL - ANALYTICAL SQL QUERIES (PHASE 3)
-- Database: PostgreSQL 12+
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 1: Total Registered Students Count
-- Description: Counts total master student profile records and distinct drive-registered students.
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_master_students
FROM students;

-- Distinct students participating in placement drives:
SELECT 
    COUNT(DISTINCT student_id) AS total_drive_registered_students
FROM student_registrations;


-- -----------------------------------------------------------------------------
-- Query 2: Company Registrations Summary
-- Description: Total student registrations grouped by company, drive name, and academic year.
-- -----------------------------------------------------------------------------
SELECT 
    c.name AS company_name,
    pd.drive_name,
    pd.academic_year,
    pd.job_role,
    pd.ctc_lpa,
    COUNT(sr.id) AS total_registrations
FROM companies c
JOIN placement_drives pd ON c.id = pd.company_id
LEFT JOIN student_registrations sr ON pd.id = sr.drive_id
GROUP BY c.id, c.name, pd.id, pd.drive_name, pd.academic_year, pd.job_role, pd.ctc_lpa
ORDER BY total_registrations DESC;


-- -----------------------------------------------------------------------------
-- Query 3: Student Registered-Company Count
-- Description: Count of distinct companies each student has registered for.
-- -----------------------------------------------------------------------------
SELECT 
    s.register_number,
    s.full_name,
    s.department,
    s.academic_year,
    COUNT(DISTINCT pd.company_id) AS registered_company_count,
    STRING_AGG(DISTINCT c.name, ', ') AS registered_companies
FROM students s
JOIN student_registrations sr ON s.id = sr.student_id
JOIN placement_drives pd ON sr.drive_id = pd.id
JOIN companies c ON pd.company_id = c.id
GROUP BY s.id, s.register_number, s.full_name, s.department, s.academic_year
ORDER BY registered_company_count DESC, s.register_number ASC;


-- -----------------------------------------------------------------------------
-- Query 4: Student Progression Count
-- Description: Count of stages cleared / progressed per student across drives.
-- -----------------------------------------------------------------------------
SELECT 
    s.register_number,
    s.full_name,
    s.department,
    pd.drive_name,
    c.name AS company_name,
    COUNT(ssr.id) AS stages_cleared_count,
    MAX(ps.stage_name) AS latest_stage_cleared
FROM students s
JOIN student_stage_results ssr ON s.id = ssr.student_id
JOIN placement_stages ps ON ssr.stage_id = ps.id
JOIN placement_drives pd ON ps.drive_id = pd.id
JOIN companies c ON pd.company_id = c.id
WHERE ssr.status = 'QUALIFIED'
GROUP BY s.id, s.register_number, s.full_name, s.department, pd.id, pd.drive_name, c.name
ORDER BY stages_cleared_count DESC;


-- -----------------------------------------------------------------------------
-- Query 5: Student Placed Count
-- Description: Total count of unique placed students and total offer count.
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT student_id) AS total_unique_placed_students,
    COUNT(id) AS total_offers_issued,
    ROUND(AVG(package_ctc)::numeric, 2) AS overall_avg_ctc_lpa,
    MAX(package_ctc) AS highest_ctc_lpa
FROM placements
WHERE status IN ('OFFERED', 'ACCEPTED');


-- -----------------------------------------------------------------------------
-- Query 6: Company-Wise Placed Count
-- Description: Total placed students, average package, and max package per company.
-- -----------------------------------------------------------------------------
SELECT 
    c.name AS company_name,
    pd.drive_name,
    pd.academic_year,
    COUNT(p.id) AS placed_student_count,
    ROUND(AVG(p.package_ctc)::numeric, 2) AS avg_package_lpa,
    MAX(p.package_ctc) AS max_package_lpa
FROM companies c
JOIN placement_drives pd ON c.id = pd.company_id
JOIN placements p ON pd.id = p.drive_id
WHERE p.status IN ('OFFERED', 'ACCEPTED')
GROUP BY c.id, c.name, pd.id, pd.drive_name, pd.academic_year
ORDER BY placed_student_count DESC, avg_package_lpa DESC;


-- -----------------------------------------------------------------------------
-- Query 7: Department-Wise Placement Statistics
-- Description: Total students, placed count, placement percentage, and average CTC by department.
-- -----------------------------------------------------------------------------
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
