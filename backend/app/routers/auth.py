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
    """Authenticates admin credentials and returns signed JWT access token."""
    admin = authenticate_admin(db, payload.email, payload.password)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": admin.email})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AdminResponse)
def get_me(current_admin: AdminUser = Depends(get_current_admin)):
    """Returns the currently authenticated admin's profile information."""
    return current_admin


@router.post("/logout")
def logout(current_admin: AdminUser = Depends(get_current_admin)):
    """Stateless logout endpoint validating current admin JWT token."""
    return {"message": f"Successfully logged out admin {current_admin.email}."}
