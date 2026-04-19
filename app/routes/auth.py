"""
Auth routes — register, login, and get current user profile.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from app.db.database import get_db
from app.schemas.user import UserRegister, UserLogin, UserOut, Token, LoginResponse
from app.services import auth_service
from app.routes.dependencies import get_current_user, security
from app.models.user import User
from app.core.security import decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    return auth_service.register_user(db, data)


@router.post("/login", response_model=LoginResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password — returns a JWT access token."""
    user, token = auth_service.login_user(db, data.email, data.password)
    return {
        "token": {
            "access_token": token,
            "token_type": "bearer"
        },
        "user": user
    }


@router.get("/verify-email")
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
