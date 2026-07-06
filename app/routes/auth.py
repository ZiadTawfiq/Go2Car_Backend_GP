"""
Auth routes — register, login, and get current user profile.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from datetime import timedelta
from app.db.database import get_db
from app.schemas.user import UserRegister, UserLogin, UserOut, Token, LoginResponse
from app.services import auth_service
from app.routes.dependencies import get_current_user, security
from app.models.user import User
from app.core.security import decode_access_token, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    return auth_service.register_user(db, data)


@router.post("/login", response_model=LoginResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password — returns a JWT access token."""
    return auth_service.login_user(db, data.email, data.password)


@router.get("/verify-email", response_model=LoginResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    return auth_service.verify_email(db, token)


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    jti = payload.get("jti")

    return auth_service.logout_user(db, jti)


@router.post("/login/guest", response_model=LoginResponse)
def login_as_guest(user_type: str = "guest"):
    """
    Guest login — returns a short-lived JWT and a placeholder user object.
    No database access required. The guest token expires in 24 hours.
    """
    guest_token = create_access_token(
        data={"sub": "0", "is_admin": False, "role": "guest"},
        expires_delta=timedelta(hours=24),
    )
    return {
        "token": {
            "access_token": guest_token,
            "token_type": "bearer",
        },
        "user": {
            "id": 0,
            "name": "Guest",
            "email": "guest@go2car.com",
            "is_admin": False,
            "user_type": user_type,
        },
    }
