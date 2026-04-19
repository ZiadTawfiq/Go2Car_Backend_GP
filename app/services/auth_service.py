"""
Authentication service — register, login, and current-user resolution.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.blacklist_token import BlacklistedToken
from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password, create_access_token

import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, status

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
    
    token = generate_verification_token()


    user = User(
        email=data.email,
        password=hash_password(data.password),
        name=data.name,
        is_admin=False,
        is_verified=False,
        verification_token=token,
        verification_token_expires_at=datetime.utcnow() + timedelta(minutes=30)
    )


    db.add(user)
    db.commit()
    db.refresh(user)

    # will replace with send_verification_email
    print(f"http://localhost:8000/api/auth/verify-email?token={token}") 

    return user


def login_user(db: Session, email: str, password: str):
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
    
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email first"
        )
    token = create_access_token({"sub": str(user.id), "is_admin": user.is_admin})

    return user,token

def generate_verification_token():
    return str(uuid.uuid4())


def verify_email(db: Session, token: str):
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    if user.is_verified:
        return {"message": "Email already verified"}

    if user.verification_token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired"
        )

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires_at = None

    db.commit()

    return {"message": "Email verified successfully"}



def logout_user(db: Session, jti: str):
    token = BlacklistedToken(jti=jti)

    db.add(token)
    db.commit()

    return {"message": "Logged out successfully"}