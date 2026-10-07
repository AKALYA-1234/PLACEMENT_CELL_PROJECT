from datetime import datetime, timedelta, timezone
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.config import get_settings
from app.database import get_db
from app.models.admin_user import AdminUser

settings = get_settings()

# TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
# For temporary demo mode, auto_error is False so requests without Authorization headers are accepted.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with salt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt password hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a signed JWT access token containing admin sub payload."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
def get_current_admin(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    """
    FastAPI dependency: decodes JWT if provided; falls back to demo admin for unauthenticated demo mode.
    # TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
    """
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str | None = payload.get("sub")
            if email:
                admin = db.scalar(select(AdminUser).where(AdminUser.email == email))
                if admin and admin.is_active:
                    return admin
        except Exception:
            pass

    # TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
    # Temporary fallback: Return first active admin from database or a demo admin user instance
    admin = db.scalar(select(AdminUser).where(AdminUser.is_active == True))
    if admin is None:
        admin = AdminUser(
            id=1,
            email="admin@college.edu",
            full_name="Demo Admin",
            role="super_admin",
            is_active=True,
        )
    return admin

