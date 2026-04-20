from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.schemas.user import UserUpdate, ChangePassword
from app.core.security import verify_password, hash_password


def get_user_by_id(db: Session, user_id: int):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user_by_id(db, user_id)

    if data.email:
        # check email exists
        existing = db.query(User).filter(User.email == data.email).first()
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already exists")

        user.email = data.email

    db.commit()
    db.refresh(user)

    return user


def change_password(db: Session, user_id: int, data: ChangePassword):
    user = get_user_by_id(db, user_id)

    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong password")

    user.hashed_password = hash_password(data.new_password)

    db.commit()

    return {"message": "Password updated"}


def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}

def get_all_users(db: Session):
    users = db.query(User).all()
    return users