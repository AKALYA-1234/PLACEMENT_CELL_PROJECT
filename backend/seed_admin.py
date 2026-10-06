"""
Seed script to create the default admin user.

Usage:
    cd backend
    python seed_admin.py
"""

import sys
import os

# Ensure the app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.admin_user import AdminUser
from app.utils.security import hash_password


def seed_admin(email: str = "admin@college.edu", password: str = "admin123", full_name: str = "Admin"):
    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing:
            print(f"Admin user '{email}' already exists. Skipping.")
            return

        admin = AdminUser(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )
        db.add(admin)
        db.commit()
        print(f"Admin user '{email}' created successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
