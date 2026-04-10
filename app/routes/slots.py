"""
Parking slot routes — view available/all slots and create new slots (admin).
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.parking_slot import ParkingSlotOut, ParkingSlotCreate
from app.services import slot_service
from app.routes.dependencies import get_current_admin

router = APIRouter(prefix="/slots", tags=["Parking Slots"])


@router.get("/available", response_model=List[ParkingSlotOut])
def available_slots(db: Session = Depends(get_db)):
    """Return all currently free parking slots."""
    return slot_service.get_available_slots(db)


@router.get("/all", response_model=List[ParkingSlotOut])
def all_slots(db: Session = Depends(get_db)):
    """Return all parking slots (occupied + free)."""
    return slot_service.get_all_slots(db)


@router.post("/", response_model=ParkingSlotOut, status_code=201)
def create_slot(
    data: ParkingSlotCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),  # admin only
):
    """Admin: add a new parking slot to the system."""
    return slot_service.create_slot(db, data)
