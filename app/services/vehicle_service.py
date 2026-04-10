"""
Vehicle service — search by plate, search by attributes, and exit logic.
"""
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.vehicle import Vehicle
from app.models.parking_record import ParkingRecord
from app.models.parking_slot import ParkingSlot


def search_by_plate(db: Session, plate: str) -> dict:
    """
    Find the active parking record for a given plate number.
    Returns slot_code and floor, or raises 404 if not found / not parked.
    """
    record = (
        db.query(ParkingRecord)
        .filter(
            ParkingRecord.plate_number == plate.upper(),
            ParkingRecord.is_active == True,
        )
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active parking record found for plate '{plate}'.",
        )
    return {"plate_number": record.plate_number, "slot_code": record.slot_code, "floor": record.floor}


def search_by_attributes(db: Session, color: Optional[str], vehicle_type: Optional[str]) -> List[dict]:
    """
    Fallback search: find all currently parked vehicles matching color and/or type.
    Returns a list of {plate_number, slot_code, floor}.
    """
    if not color and not vehicle_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one search attribute: color or type.",
        )

    query = db.query(Vehicle)
    if color:
        query = query.filter(Vehicle.color.ilike(f"%{color}%"))
    if vehicle_type:
        query = query.filter(Vehicle.type.ilike(f"%{vehicle_type}%"))

    vehicles = query.all()
    if not vehicles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vehicles found matching the given attributes.",
        )

    results = []
    for v in vehicles:
        record = (
            db.query(ParkingRecord)
            .filter(
                ParkingRecord.plate_number == v.plate_number,
                ParkingRecord.is_active == True,
            )
            .first()
        )
        if record:
            results.append(
                {"plate_number": v.plate_number, "slot_code": record.slot_code, "floor": record.floor}
            )

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicles found but none are currently parked.",
        )
    return results


def exit_vehicle(db: Session, plate: str) -> dict:
    """
    Process a vehicle exit:
      1. Find the active parking record.
      2. Mark it as inactive and set exit_time.
      3. Free the corresponding parking slot.
    """
    record = (
        db.query(ParkingRecord)
        .filter(
            ParkingRecord.plate_number == plate.upper(),
            ParkingRecord.is_active == True,
        )
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active parking session found for plate '{plate}'.",
        )

    # Update the record
    record.is_active = False
    record.exit_time = datetime.now(timezone.utc)

    # Free the slot
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_code == record.slot_code).first()
    if slot:
        slot.is_occupied = False

    db.commit()
    return {"message": f"Vehicle '{plate}' has exited. Slot '{record.slot_code}' is now free."}
