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

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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
        user_type= data.user_type,
        is_verified=False,
        verification_token=token,
        verification_token_expires_at=datetime.utcnow() + timedelta(minutes=30)
    )


    db.add(user)
    db.commit()
    db.refresh(user)

    # will replace with send_verification_email
    print(f"http://localhost:8000/auth/verify-email?token={token}") 
    send_verification_email(data.email, token)

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

    return {
        "token": {
            "access_token": token,
            "token_type": "bearer"
        },
        "user": user
    }


def generate_verification_token():
    return str(uuid.uuid4())


def send_verification_email(to_email: str, token: str):
    verification_link = f"https://go2carbackendgp-production.up.railway.app/auth/verify-email?token={token}"
    # verification_link = f"http://localhost:8000/auth/verify-email?token={token}"

    message = Mail(
        from_email='temptarek1899@gmail.com',
        to_emails= to_email,
        subject='Verify your Go2Car account',
        html_content=f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            
            <h2 style="color:#2c3e50;">🚗 Go2Car</h2>

            <h3>Verify your account</h3>

            <p>Welcome to <b>Go2Car</b> 👋</p>

            <p>Please click the button below to verify your email:</p>

            <a href="{verification_link}" 
            style="
                    display:inline-block;
                    padding:10px 20px;
                    background-color:#007bff;
                    color:white;
                    text-decoration:none;
                    border-radius:5px;
                    margin-top:10px;
            ">
            Verify Email
            </a>

            <p style="margin-top:20px; font-size:12px; color:gray;">
                If you didn’t create this account, ignore this email.
            </p>

        </div>
        """
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
    except Exception as e:
        print("Email error:", e)


def verify_email(db: Session, token: str):
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    if user.verification_token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired"
        )

    if not user.is_verified:
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires_at = None
        db.commit()
        db.refresh(user)

    access_token = create_access_token({
        "sub": str(user.id),
        "is_admin": user.is_admin
    })

    return {
        "token": {
            "access_token": access_token,
            "token_type": "bearer"
        },
        "user": user
    }


def logout_user(db: Session, jti: str):
    token = BlacklistedToken(jti=jti)

    db.add(token)
    db.commit()

    return {"message": "Logged out successfully"}