from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate, ChangePassword
from app.services.user_service import (
    update_current_user,
    change_current_user_password,
    delete_current_user,
)

from app.routes.dependencies import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================
# 👤 USER ROUTES
# =========================

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_current_user(db, current_user.id, data)


@router.put("/me/password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return change_current_user_password(db, current_user.id, data)


@router.delete("/me")
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_current_user(db, current_user.id)