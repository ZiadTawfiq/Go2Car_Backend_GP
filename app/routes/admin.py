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
    admin_delete_user, get_peak_hours, get_heatmap_data, get_analytics_history,
    export_analytics_pdf,
)
from app.schemas.user import AdminUpdateUser
from app.services.admin_service import admin_update_user
from app.services import admin_service

from app.routes.dependencies import get_current_admin
from app.services.admin_service import get_analytics_summary

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

@router.get(
    "/analytics/summary",
    summary="Analytics summary",
    description="Get parking KPIs and occupancy statistics"
)
def analytics_summary(
    db: Session = Depends(get_db)
):
    return get_analytics_summary(db)

@router.get(
    "/analytics/peak-hours",
    summary="Peak hours analytics",
    description="Get hourly parking activity statistics"
)
def peak_hours(
    db: Session = Depends(get_db)
):
    return get_peak_hours(db)

@router.get(
    "/analytics/heatmap",
    summary="Parking heatmap",
    description="Per-slot parking usage analytics"
)
def heatmap(
    db: Session = Depends(get_db)
):
    return get_heatmap_data(db)

@router.get(
    "/analytics/history",
    summary="Parking history analytics",
    description="Get historical parking activity timeline"
)
def analytics_history(
    db: Session = Depends(get_db)
):
    return get_analytics_history(db)

@router.get(
    "/analytics/export/pdf",
    summary="Export PDF report",
    description="Export parking analytics as PDF"
)
def export_pdf(
    db: Session = Depends(get_db)
):
    return export_analytics_pdf(db)