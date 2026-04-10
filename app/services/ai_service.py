"""
AI service — handles the core detection flow:
  1. Save or retrieve the vehicle.
  2. Guard against duplicate active parking sessions.
  3. Find or auto-create the parking slot.
  4. Create the parking record.
  5. Mark the slot as occupied.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.vehicle import Vehicle
from app.models.parking_slot import ParkingSlot
from app.models.parking_record import ParkingRecord
from app.schemas.ai import AIDetectRequest


def process_detection(db: Session, data: AIDetectRequest) -> dict:
    """
    Full detection pipeline called by the AI module.
    Idempotent: safe to call again if the vehicle is already parked.
    """
    plate = data.plate.upper()

    # ── 1. Upsert vehicle ──────────────────────────────────────────────────
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if not vehicle:
        vehicle = Vehicle(
            plate_number=plate,
            color=data.color,
            type=data.type,
        )
        db.add(vehicle)
        db.flush()  # get ID without committing yet
    else:
        # Update attributes if the AI provides richer info than what's stored
        if data.color and not vehicle.color:
            vehicle.color = data.color
        if data.type and not vehicle.type:
            vehicle.type = data.type

    # ── 2. Check for existing active session ──────────────────────────────
    active_record = (
        db.query(ParkingRecord)
        .filter(ParkingRecord.plate_number == plate, ParkingRecord.is_active == True)
        .first()
    )
    if active_record:
        # Already parked — return current location (idempotent)
        db.commit()
        return {
            "message": "Vehicle is already parked.",
            "plate": plate,
            "slot_code": active_record.slot_code,
            "floor": active_record.floor,
        }

    # ── 3. Find or create the parking slot ────────────────────────────────
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_code == data.slot_code).first()
    if not slot:
        slot = ParkingSlot(slot_code=data.slot_code, floor=data.floor, is_occupied=False)
        db.add(slot)
        db.flush()

    if slot.is_occupied:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slot '{data.slot_code}' is already occupied by another vehicle.",
        )

    # ── 4. Create parking record ───────────────────────────────────────────
    record = ParkingRecord(
        plate_number=plate,
        slot_code=data.slot_code,
        floor=data.floor,
        is_active=True,
    )
    db.add(record)

    # ── 5. Mark slot as occupied ───────────────────────────────────────────
    slot.is_occupied = True

    db.commit()

    return {
        "message": "Vehicle detected and parked successfully.",
        "plate": plate,
        "slot_code": data.slot_code,
        "floor": data.floor,
    }
