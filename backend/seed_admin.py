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


def seed_admin(username: str = "admin", password: str = "admin123"):
    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing:
            print(f"Admin user '{username}' already exists. Skipping.")
            return

        admin = AdminUser(
            username=username,
            hashed_password=hash_password(password),
        )
        db.add(admin)
        db.commit()
        print(f"Admin user '{username}' created successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
