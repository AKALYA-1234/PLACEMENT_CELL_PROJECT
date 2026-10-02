from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.admin_user import AdminUser
from app.utils.security import verify_password


def authenticate_admin(db: Session, email: str, password: str) -> AdminUser | None:
    """Verify admin credentials against database email and password hash. Returns AdminUser or None."""
    admin = db.scalar(select(AdminUser).where(AdminUser.email == email))
    if admin is None:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin
