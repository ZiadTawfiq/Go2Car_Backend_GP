"""
Admin service — summary analytics for the parking facility.
"""
from datetime import datetime, timedelta
from http.client import HTTPException

from sqlalchemy.orm import Session
from starlette import status

from app.models import User
from app.models.parking_slot import ParkingSlot
from app.schemas.user import AdminUpdateUser, UserRegister
from app.services.auth_service import generate_verification_token
from app.services.user_service import get_user_by_id
from app.core.security import hash_password


def get_summary(db: Session) -> dict:
    """
    Return a high-level summary of parking facility usage.
    """
    total = db.query(ParkingSlot).count()
    occupied = db.query(ParkingSlot).filter(ParkingSlot.is_occupied == True).count()
    available = total - occupied
    occupancy_rate = round((occupied / total * 100), 2) if total > 0 else 0.0

    return {
        "total_slots": total,
        "occupied_slots": occupied,
        "available_slots": available,
        "occupancy_rate_percent": occupancy_rate,
    }

def get_all_users(db: Session):
    return db.query(User).all()


def create_admin_account(db: Session, data: UserRegister) -> User:
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
        is_admin=True,
        is_verified=False,
        verification_token=token,
        verification_token_expires_at=datetime.utcnow() + timedelta(minutes=30),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"http://localhost:8000/api/auth/verify-email?token={token}")

    return user


def admin_delete_user(db: Session, admin_user: User, user_id: int):
    if not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": f"User {user_id} deleted by admin"}

def admin_update_user(db: Session, user_id: int, data: AdminUpdateUser):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = data.email

    if data.name:
        user.name = data.name

    if data.is_admin is not None:
        user.is_admin = data.is_admin

    db.commit()
    db.refresh(user)

    return user