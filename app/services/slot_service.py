"""
Slot service — query available and all parking slots.
"""
from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.parking_slot import ParkingSlot
from app.schemas.parking_slot import ParkingSlotCreate


def get_available_slots(db: Session) -> List[ParkingSlot]:
    """Return all slots that are currently free."""
    return db.query(ParkingSlot).filter(ParkingSlot.is_occupied == False).all()


def get_all_slots(db: Session) -> List[ParkingSlot]:
    """Return every slot regardless of occupancy."""
    return db.query(ParkingSlot).all()


def create_slot(db: Session, data: ParkingSlotCreate) -> ParkingSlot:
    """
    Admin helper: create a new parking slot.
    Raises 400 if slot_code already exists.
    """
    existing = db.query(ParkingSlot).filter(ParkingSlot.slot_code == data.slot_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Slot '{data.slot_code}' already exists.",
        )
    slot = ParkingSlot(slot_code=data.slot_code, section_id=data.section_id)
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot
