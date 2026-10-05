"""
One-time script to fix students whose department is 'General'
by decoding it from their register number.
Run from: d:/AIWF PROJECTS/PLACEMENT-PROJECT/backend
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models import Student
from sqlalchemy import select
from app.services.excel_parser.department_decoder import decode_department_from_register

db = SessionLocal()

students = db.scalars(select(Student).where(Student.department == "General")).all()
fixed = 0

for s in students:
    decoded = decode_department_from_register(s.register_number)
    if decoded:
        print(f"  {s.register_number} ({s.full_name}): General → {decoded}")
        s.department = decoded
        fixed += 1

db.commit()
db.close()
print(f"\nFixed {fixed} student(s) out of {len(students)} with 'General' department.")
