"""
Admin routes — protected summary endpoint.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserRegister
from app.services.admin_service import (
    get_all_users,
    create_admin_account,
    admin_delete_user,
)
from app.schemas.user import AdminUpdateUser
from app.services.admin_service import admin_update_user
from app.services import admin_service

from app.routes.dependencies import get_current_admin


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# =========================
#  ADMIN ROUTES
# =========================

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin),
):
    return admin_service.get_summary(db)


@router.get("/users", response_model=List[UserOut])
def get_users(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin),
):
    return get_all_users(db)


@router.post("/users", response_model=UserOut)
def create_admin(
    data: UserRegister,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return create_admin_account(db, data)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return admin_delete_user(db, current_admin, user_id)

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: AdminUpdateUser,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return admin_update_user(db, user_id, data)

