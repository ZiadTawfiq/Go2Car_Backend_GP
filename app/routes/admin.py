"""
Admin routes — protected summary endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import admin_service
from app.routes.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),  # requires admin JWT
):
    """
    📊 Admin dashboard summary:
    - Total slots
    - Occupied slots
    - Available slots
    - Occupancy rate (%)
    """
    return admin_service.get_summary(db)
