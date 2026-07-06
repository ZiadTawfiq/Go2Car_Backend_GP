"""
Slot service — query available and all parking slots.
"""
import os
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from fastapi import HTTPException, status

# Base directory for map images (relative to project root)
MAPS_DIR = Path("static/maps")

from app.models import ParkingSlot, ParkingSection
from app.schemas.parking_slot import ParkingSlotCreate, SlotOccupancyOut


def get_available_slots(db: Session) -> List[ParkingSlot]:
    """Return all slots that are currently free and not booked."""
    from app.models.reservation import Reservation, ReservationStatus
    
    booked_slot_ids = db.query(Reservation.slot_id).filter(
        Reservation.status == ReservationStatus.active
    ).subquery()

    return db.query(ParkingSlot).filter(
        ParkingSlot.is_occupied == False,
        ~ParkingSlot.id.in_(booked_slot_ids)
    ).options(
        joinedload(ParkingSlot.section).joinedload(ParkingSection.floor)
    ).all()


def get_all_slots(db: Session) -> List[ParkingSlot]:
    """Return every slot that is not occupied."""
    return db.query(ParkingSlot).filter(
        ParkingSlot.is_occupied == False
    ).options(
        joinedload(ParkingSlot.section).joinedload(ParkingSection.floor)
    ).all()


def get_slot_by_id(db: Session, slot_id: int):
    return db.query(ParkingSlot).options(
        joinedload(ParkingSlot.section).joinedload(ParkingSection.floor)
    ).filter(ParkingSlot.id == slot_id).first()


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


def get_occupancy(db: Session):
    result = db.query(
        func.count(ParkingSlot.id).label("total"),
        func.sum(case((ParkingSlot.is_occupied == True, 1), else_=0)).label("occupied")
    ).one()

    total = result.total or 0
    occupied = result.occupied or 0
    free = total - occupied

    percentage = (occupied / total * 100) if total > 0 else 0

    return {
        "total_slots": total,
        "occupied_slots": occupied,
        "free_slots": free,
        "occupancy_percentage": round(percentage, 2)
    }



def update_slot_type(db: Session, slot_id: int, slot_type: str):
    slot = db.query(ParkingSlot).filter(ParkingSlot.id == slot_id).first()
    
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    slot.slot_type = slot_type
    db.commit()
    db.refresh(slot)

    return slot


def get_slot_map(db: Session, slot_id: int) -> dict:
    """Return the map image path for a given slot."""
    slot = get_slot_by_id(db, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    section_code = slot.section.section_code  # e.g. "F1_A1"

    # Use absolute path relative to project root (works regardless of Railway CWD)
    project_root = Path(__file__).resolve().parent.parent.parent
    maps_dir = project_root / "static" / "maps"
    map_file = maps_dir / f"{section_code}.jpg"

    if map_file.exists():
        map_path = f"/static/maps/{section_code}.jpg"
    else:
        map_path = f"/static/maps/map.jpg"

    return {
        "success": True,
        "data": {
            "map_path": map_path,
            "slot": slot.slot_code,
        }
    }
