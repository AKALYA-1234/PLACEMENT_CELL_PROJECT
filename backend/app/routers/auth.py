from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import LoginRequest, TokenResponse, AdminResponse
from app.services.auth_service import authenticate_admin
from app.utils.security import create_access_token, get_current_admin

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate admin and return a JWT access token."""
    admin = authenticate_admin(db, payload.username, payload.password)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(data={"sub": admin.username})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AdminResponse)
def get_me(current_admin: AdminUser = Depends(get_current_admin)):
    """Return the currently logged-in admin's info."""
    return current_admin
