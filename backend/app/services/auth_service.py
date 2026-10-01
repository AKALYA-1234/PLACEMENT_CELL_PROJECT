from sqlalchemy.orm import Session

from app.models.admin_user import AdminUser
from app.utils.security import verify_password


def authenticate_admin(db: Session, username: str, password: str) -> AdminUser | None:
    """Verify admin credentials. Returns AdminUser or None."""
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if admin is None:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    return admin
