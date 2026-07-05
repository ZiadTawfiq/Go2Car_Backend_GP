"""
Parking slot routes — view available/all slots and create new slots (admin).
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.parking_slot import ParkingSlotOut, ParkingSlotCreate, SlotOccupancyOut, SlotStatusUpdate
from app.services import slot_service
from app.routes.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter(prefix="/slots", tags=["Parking Slots"])


@router.get("/available", response_model=List[ParkingSlotOut])
def available_slots(db: Session = Depends(get_db)):
    """Return all currently free parking slots. [public]"""
    return slot_service.get_available_slots(db)


@router.get("/all", response_model=List[ParkingSlotOut])
def all_slots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return all parking slots (occupied + free). [JWT required]"""
    return slot_service.get_all_slots(db)


@router.get("/occupancy", response_model=SlotOccupancyOut)
def get_occupancy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return occupancy summary. [JWT required]"""
    return slot_service.get_occupancy(db)


@router.get("/{slot_id}/map")
def get_slot_map(
    slot_id: int,
    db: Session = Depends(get_db)
):
    """Return the map image path for a specific slot. [public]"""
    return slot_service.get_slot_map(db, slot_id)


@router.get("/{slot_id}", response_model=ParkingSlotOut)
def get_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return one slot (occupied + free). [JWT required]"""
    slot = slot_service.get_slot_by_id(db, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot


@router.post("/", response_model=ParkingSlotOut, status_code=201)
def create_slot(
    data: ParkingSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Admin: add a new parking slot to the system. [JWT + admin]"""
    return slot_service.create_slot(db, data)


@router.patch("/{slot_id}", response_model=ParkingSlotOut)
def change_slot_status(
    slot_id: int,
    data: SlotStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Admin: manually override a slot's occupancy status. [JWT + admin]"""
    return slot_service.update_slot_status(db, slot_id, data.is_occupied)