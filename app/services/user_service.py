from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from starlette import status

from app.models.user import User
from app.schemas.user import UserUpdate, ChangePassword, UserRegister
from app.core.security import verify_password, hash_password
from app.services.auth_service import generate_verification_token



def get_user_by_id(db: Session, user_id: int):
    return db.get(User, user_id)


# =========================
# User
# =========================
def get_current_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_current_user(db: Session, user_id: int, data: UserUpdate):
    user = get_current_user(db, user_id)

    # Email update
    if data.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = data.email

    # Name update
    if data.name:
        user.name = data.name

    db.commit()
    db.refresh(user)

    return user


def change_current_user_password(db: Session, user_id: int, data: ChangePassword):
    user = get_current_user(db, user_id)

    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Wrong password")

    if data.old_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different")

    user.password = hash_password(data.new_password)

    db.commit()

    return {"message": "Password updated successfully"}


def delete_current_user(db: Session, user_id: int):
    user = get_current_user(db, user_id)

    db.delete(user)
    db.commit()

    return {"message": "Account deleted successfully"}

