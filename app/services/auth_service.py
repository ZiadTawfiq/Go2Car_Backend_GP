"""
Authentication service — register, login, and current-user resolution.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, data: UserRegister) -> User:
    """
    Create a new user after checking that the email is not already taken.
    Raises 400 if the email already exists.
    """
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )
    user = User(
        email=data.email,
        password=hash_password(data.password),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, email: str, password: str) -> str:
    """
    Verify credentials and return a JWT access token.
    Raises 401 on invalid credentials.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    return create_access_token({"sub": str(user.id), "is_admin": user.is_admin})

