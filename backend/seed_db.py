import hashlib
from datetime import date, datetime
from app.database import SessionLocal, engine, Base
from app.models import (
    AdminUser, Student, Company, PlacementDrive, PlacementStage,
    StudentRegistration, StudentStageResult, Placement, ImportLog
)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def seed():
    db = SessionLocal()
    try:
        print("Clearing existing data...")
        db.query(Placement).delete()
        db.query(StudentStageResult).delete()
        db.query(StudentRegistration).delete()
        db.query(PlacementStage).delete()
        db.query(ImportLog).delete()
        db.query(PlacementDrive).delete()
        db.query(Company).delete()
        db.query(Student).delete()
        db.query(AdminUser).delete()
        db.commit()

        print("Seeding Admin User...")
        admin = AdminUser(
            email="admin@college.edu",
            password_hash=hash_password("admin123"),
            full_name="Placement Director",
            role="SUPER_ADMIN",
            is_active=True
        )
        db.add(admin)

        print("Seeding Students...")
        students_data = [
            # reg, name, dept, email, mob, gender, acc, cgpa, yr
            ("7376232AD101", "AATHINI S S", "Artificial Intelligence and Data Science", "aathini.ad23@bitsathy.ac.in", "9345795447", "Female", "Day Scholar", 8.75, "2026-2027"),
            ("7376232AD104", "ABINISHA A S", "Artificial Intelligence and Data Science", "abinisha.ad23@bitsathy.ac.in", "8072132817", "Female", "Hosteller", 8.42, "2026-2027"),
            ("7376242AD501", "ABIRAMI N M", "Artificial Intelligence and Data Science", "abiraminm.ad23@bitsathy.ac.in", "6380374104", "Female", "Day Scholar", 8.90, "2026-2027"),
            ("7376232AD112", "ASMA BANU I", "Artificial Intelligence and Data Science", "asmabanu.ad23@bitsathy.ac.in", "9677617836", "Female", "Hosteller", 8.65, "2026-2027"),
            ("7376232AD143", "GURUNISHA S", "Artificial Intelligence and Data Science", "gurunisha.ad23@bitsathy.ac.in", "9876543210", "Female", "Hosteller", 8.12, "2026-2027"),
            ("7376232AD191", "Mahavishnu K", "Artificial Intelligence and Data Science", "mahavishnu.ad23@bitsathy.ac.in", "9123456789", "Male", "Hosteller", 9.15, "2026-2027"),
            ("7376232AD195", "Mohammed Afeef M", "Artificial Intelligence and Data Science", "afeef.ad23@bitsathy.ac.in", "9443322110", "Male", "Hosteller", 8.88, "2026-2027"),
            ("7376232AD252", "SHARVESH RAMALINGAM", "Artificial Intelligence and Data Science", "sharvesh.ad23@bitsathy.ac.in", "9554433221", "Male", "Day Scholar", 8.35, "2026-2027"),

            # Computer Science and Engineering
            ("7376231CS191", "KAMALESH K", "Computer Science and Engineering", "kamalesh.cs23@bitsathy.ac.in", "6369026251", "Male", "Hosteller", 8.80, "2026-2027"),
            ("7376231CS313", "SOBIKA S M", "Computer Science and Engineering", "sobika.cs23@bitsathy.ac.in", "9751515795", "Female", "Day Scholar", 9.20, "2026-2027"),
            ("7376231CS333", "THAYANITHI S", "Computer Science and Engineering", "thayanithi.cs23@bitsathy.ac.in", "9887766554", "Male", "Hosteller", 9.40, "2026-2027"),
            ("7376231CS107", "ADHAVAN SE V", "Computer Science and Engineering", "adhavan.cs23@bitsathy.ac.in", "9776655443", "Male", "Hosteller", 8.95, "2026-2027"),
            ("7376231CS148", "DIVYAPRAKASH R", "Computer Science and Engineering", "divyaprakash.cs23@bitsathy.ac.in", "9665544332", "Male", "Day Scholar", 8.10, "2026-2027"),

            # Electronics and Communication Engineering
            ("7376231EC173", "JOTHIKA S", "Electronics and Communication Engineering", "jothika.ec23@bitsathy.ac.in", "7200910155", "Female", "Day Scholar", 8.50, "2026-2027"),
            ("7376231EC134", "DHANUSRI K R R", "Electronics and Communication Engineering", "dhanusri.ec23@bitsathy.ac.in", "8825608620", "Female", "Day Scholar", 9.05, "2026-2027"),
            ("7376231EC158", "HARISHMITHA R", "Electronics and Communication Engineering", "harishmitha.ec23@bitsathy.ac.in", "9332211009", "Female", "Hosteller", 8.70, "2026-2027"),
            ("7376231EC140", "DINESH S", "Electronics and Communication Engineering", "dinesh.ec23@bitsathy.ac.in", "9221100998", "Male", "Day Scholar", 8.60, "2026-2027"),
            ("7376231EC192", "KOUSIK A B", "Electronics and Communication Engineering", "kousik.ec23@bitsathy.ac.in", "9110099887", "Male", "Hosteller", 8.75, "2026-2027"),

            # Information Technology
            ("7376232IT114", "ARVINDH S", "Information Technology", "arvindh.it23@bitsathy.ac.in", "9626163456", "Male", "Day Scholar", 8.25, "2026-2027"),
            ("7376232IT143", "GIRISH ASHOK GAIKWAD A", "Information Technology", "girish.it23@bitsathy.ac.in", "9998887776", "Male", "Hosteller", 8.90, "2026-2027"),
            ("7376232IT257", "Shashwath V R", "Information Technology", "shashwath.it23@bitsathy.ac.in", "9888777665", "Male", "Day Scholar", 8.65, "2026-2027"),
            ("7376231SE116", "GAYATHIRI E", "Information Technology", "gayathiri.se23@bitsathy.ac.in", "9777666554", "Female", "Hosteller", 9.30, "2026-2027"),

            # Computer Science and Business Systems
            ("7376232CB156", "SUDHARSHANA M K", "Computer Science and Business Systems", "sudharshana.cb23@bitsathy.ac.in", "8248932487", "Female", "Day Scholar", 8.55, "2026-2027"),
        ]

        students_dict = {}
        for reg, name, dept, email, mob, gender, acc, cgpa, yr in students_data:
            s = Student(
                register_number=reg, full_name=name, department=dept,
                email=email, mobile_number=mob, gender=gender,
                accommodation_type=acc, cgpa=cgpa, academic_year=yr
            )
            db.add(s)
            students_dict[reg] = s
        db.flush()

        print("Seeding Companies...")
        c_netgear = Company(name="Netgear", industry="Networking & Hardware", website="https://www.netgear.com", contact_email="campus@netgear.com")
        c_presidio = Company(name="Presidio", industry="Cloud & IT Services", website="https://www.presidio.com", contact_email="careers@presidio.com")
        c_soliton = Company(name="Soliton Technologies", industry="Embedded Systems & Test Automation", website="https://www.solitontech.com", contact_email="hr@solitontech.com")
        
        db.add_all([c_netgear, c_presidio, c_soliton])
        db.flush()

        print("Seeding Placement Drives...")
        d_netgear = PlacementDrive(company_id=c_netgear.id, drive_name="Netgear Placement Drive 2026", academic_year="2026-2027", job_role="Software Engineer", ctc_lpa=12.0, drive_date=date(2026, 7, 23), status="COMPLETED")
        d_presidio = PlacementDrive(company_id=c_presidio.id, drive_name="Presidio Recruitment Drive 2026", academic_year="2026-2027", job_role="Cloud Engineer", ctc_lpa=9.5, drive_date=date(2026, 8, 10), status="COMPLETED")
        d_soliton = PlacementDrive(company_id=c_soliton.id, drive_name="Soliton Campus Drive 2026", academic_year="2026-2027", job_role="Systems Engineer", ctc_lpa=10.5, drive_date=date(2026, 8, 25), status="COMPLETED")

        db.add_all([d_netgear, d_presidio, d_soliton])
        db.flush()

        print("Seeding Placement Stages...")
        # Netgear Stages
        s_n1 = PlacementStage(drive_id=d_netgear.id, stage_order=1, stage_name="Registered", normalized_category="REGISTERED")
        s_n2 = PlacementStage(drive_id=d_netgear.id, stage_order=2, stage_name="Round 2 - Technical Screening", normalized_category="PROGRESSION")
        s_n3 = PlacementStage(drive_id=d_netgear.id, stage_order=3, stage_name="Round 3 - Coding Round", normalized_category="PROGRESSION")
        s_n4 = PlacementStage(drive_id=d_netgear.id, stage_order=4, stage_name="Round 4 - Final Selects", normalized_category="PLACED")

        # Presidio Stages
        s_p1 = PlacementStage(drive_id=d_presidio.id, stage_order=1, stage_name="Round 1 - Aptitude Test", normalized_category="REGISTERED")
        s_p2 = PlacementStage(drive_id=d_presidio.id, stage_order=2, stage_name="Round 2 - Technical Interview", normalized_category="PROGRESSION")
        s_p3 = PlacementStage(drive_id=d_presidio.id, stage_order=3, stage_name="Offer List", normalized_category="PLACED")

        # Soliton Stages
        s_s1 = PlacementStage(drive_id=d_soliton.id, stage_order=1, stage_name="Round 1 - Online Test", normalized_category="REGISTERED")
        s_s2 = PlacementStage(drive_id=d_soliton.id, stage_order=2, stage_name="Round 2 - Lab Test", normalized_category="PROGRESSION")
        s_s3 = PlacementStage(drive_id=d_soliton.id, stage_order=3, stage_name="Round 3 - Technical Interview 1", normalized_category="PROGRESSION")
        s_s4 = PlacementStage(drive_id=d_soliton.id, stage_order=4, stage_name="Round 4 - Technical Interview 2", normalized_category="PROGRESSION")
        s_s5 = PlacementStage(drive_id=d_soliton.id, stage_order=5, stage_name="Design round 5 - System Design", normalized_category="PROGRESSION")
        s_s6 = PlacementStage(drive_id=d_soliton.id, stage_order=6, stage_name="OFFER List", normalized_category="PLACED")

        db.add_all([s_n1, s_n2, s_n3, s_n4, s_p1, s_p2, s_p3, s_s1, s_s2, s_s3, s_s4, s_s5, s_s6])
        db.flush()

        print("Seeding Student Registrations, Stage Results, and Placements...")

        # Netgear Registrations & Results
        netgear_students = list(students_dict.values())
        for s in netgear_students:
            reg = StudentRegistration(drive_id=d_netgear.id, student_id=s.id)
            db.add(reg)
            db.flush()
            # Stage 1 result
            sr1 = StudentStageResult(stage_id=s_n1.id, student_id=s.id, registration_id=reg.id, status="QUALIFIED")
            db.add(sr1)

        # Netgear Round 4 Selects (SOBIKA S M & DHANUSRI K R R)
        for reg_no in ["7376231CS313", "7376231EC134"]:
            s = students_dict[reg_no]
            reg = db.query(StudentRegistration).filter_by(drive_id=d_netgear.id, student_id=s.id).first()
            sr4 = StudentStageResult(stage_id=s_n4.id, student_id=s.id, registration_id=reg.id, status="QUALIFIED")
            db.add(sr4)
            p = Placement(drive_id=d_netgear.id, student_id=s.id, registration_id=reg.id, stage_id=s_n4.id, package_ctc=12.0, offer_date=date(2026, 7, 24), status="ACCEPTED")
            db.add(p)

        # Presidio Registrations & Results
        for s in netgear_students[:15]:
            reg = StudentRegistration(drive_id=d_presidio.id, student_id=s.id)
            db.add(reg)
            db.flush()
            sr1 = StudentStageResult(stage_id=s_p1.id, student_id=s.id, registration_id=reg.id, status="QUALIFIED")
            db.add(sr1)

        # Presidio Offers (THAYANITHI S, GIRISH ASHOK GAIKWAD A, Mahavishnu K)
        for reg_no in ["7376231CS333", "7376232IT143", "7376232AD191"]:
            s = students_dict[reg_no]
            reg = db.query(StudentRegistration).filter_by(drive_id=d_presidio.id, student_id=s.id).first()
            if not reg:
                reg = StudentRegistration(drive_id=d_presidio.id, student_id=s.id)
                db.add(reg)
                db.flush()
            sr3 = StudentStageResult(stage_id=s_p3.id, student_id=s.id, registration_id=reg.id, status="QUALIFIED")
            db.add(sr3)
            p = Placement(drive_id=d_presidio.id, student_id=s.id, registration_id=reg.id, stage_id=s_p3.id, package_ctc=9.5, offer_date=date(2026, 8, 11), status="OFFERED")
            db.add(p)

        # Soliton Registrations & Results
        for s in netgear_students:
            reg = StudentRegistration(drive_id=d_soliton.id, student_id=s.id)
            db.add(reg)
            db.flush()
            sr1 = StudentStageResult(stage_id=s_s1.id, student_id=s.id, registration_id=reg.id, status="QUALIFIED")
            db.add(sr1)

        # Soliton Offers (GAYATHIRI E, HARISHMITHA R, DINESH S, ADHAVAN SE V, SHARVESH RAMALINGAM, Mohammed Afeef M, KOUSIK A B)
        soliton_placed = ["7376231SE116", "7376231EC158", "7376231EC140", "7376231CS107", "7376232AD252", "7376232AD195", "7376231EC192"]
        for reg_no in soliton_placed:
            s = students_dict[reg_no]
            reg = db.query(StudentRegistration).filter_by(drive_id=d_soliton.id, student_id=s.id).first()
            sr6 = StudentStageResult(stage_id=s_s6.id, student_id=s.id, registration_id=reg.id, status="QUALIFIED")
            db.add(sr6)
            p = Placement(drive_id=d_soliton.id, student_id=s.id, registration_id=reg.id, stage_id=s_s6.id, package_ctc=10.5, offer_date=date(2026, 8, 26), status="ACCEPTED")
            db.add(p)

        print("Seeding Import Logs...")
        l1 = ImportLog(filename="Netgear - Roundwise.xlsx", file_type="EXCEL", company_id=c_netgear.id, drive_id=d_netgear.id, stage_id=s_n1.id, total_rows=335, imported_rows=335, failed_rows=0, status="SUCCESS", imported_by="admin@college.edu")
        l2 = ImportLog(filename="PRESIDIO.xlsx", file_type="EXCEL", company_id=c_presidio.id, drive_id=d_presidio.id, stage_id=s_p1.id, total_rows=419, imported_rows=419, failed_rows=0, status="SUCCESS", imported_by="admin@college.edu")
        l3 = ImportLog(filename="Soliton Roundwise Details.xlsx", file_type="EXCEL", company_id=c_soliton.id, drive_id=d_soliton.id, stage_id=s_s1.id, total_rows=520, imported_rows=520, failed_rows=0, status="SUCCESS", imported_by="admin@college.edu")

        db.add_all([l1, l2, l3])
        db.commit()

        print("\nDatabase seeded successfully!")
        print(f"Summary:")
        print(f"  - Admin Users: {db.query(AdminUser).count()}")
        print(f"  - Students: {db.query(Student).count()}")
        print(f"  - Companies: {db.query(Company).count()}")
        print(f"  - Placement Drives: {db.query(PlacementDrive).count()}")
        print(f"  - Placement Stages: {db.query(PlacementStage).count()}")
        print(f"  - Student Registrations: {db.query(StudentRegistration).count()}")
        print(f"  - Student Stage Results: {db.query(StudentStageResult).count()}")
        print(f"  - Placements: {db.query(Placement).count()}")
        print(f"  - Import Logs: {db.query(ImportLog).count()}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
