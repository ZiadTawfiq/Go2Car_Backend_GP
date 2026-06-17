"""
AI service — handles two flows:

  A) park_vehicle      : direct park endpoint (POST /ai/park)
                         called when caller already knows a car is present.
  B) handle_slot_scan  : scan-result endpoint (POST /ai/scan-result)
                         called by the external AI vision service after
                         processing a camera snapshot.

Shared pipeline when a car IS present:
  1. Save or retrieve the vehicle.
  2. Guard against duplicate active parking sessions.
  3. Look up the parking slot (404 if not pre-configured — no ghost slots).
  4. Guard against slot already occupied by another vehicle.
  5. Create the parking record (vehicle_id FK + slot_id FK).
  6. Mark the slot as occupied.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.vehicle import Vehicle
from app.models.parking_slot import ParkingSlot
from app.models.parking_record import ParkingRecord
from app.schemas.ai import ParkVehicleRequest, SlotScanResult


# ── Shared internal helper ─────────────────────────────────────────────────────

def _assign_vehicle_to_slot(
    db: Session,
    plate: str,
    slot_code: str,
    color: str | None,
    vehicle_type: str | None,
) -> dict:
    """
    Core pipeline: upsert vehicle → guard duplicates → link to slot → create record.
    Returns a summary dict (not a Pydantic model — callers wrap it themselves).
    """

    # 1. Upsert vehicle ────────────────────────────────────────────────────────
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if not vehicle:
        vehicle = Vehicle(
            plate_number=plate,
            color=color,
            vehicle_type=vehicle_type,
        )
        db.add(vehicle)
        db.flush()  # get vehicle.id before commit
    else:
        # Enrich existing record if new info is available
        if color and not vehicle.color:
            vehicle.color = color
        if vehicle_type and not vehicle.vehicle_type:
            vehicle.vehicle_type = vehicle_type

    # 2. Guard duplicate active session ────────────────────────────────────────
    active_record = (
        db.query(ParkingRecord)
        .filter(
            ParkingRecord.vehicle_id == vehicle.id,
            ParkingRecord.is_active == True,
        )
        .first()
    )
    if active_record:
        # Already parked — idempotent, return current location
        db.commit()
        current_slot = db.query(ParkingSlot).filter(
            ParkingSlot.id == active_record.slot_id
        ).first()
        return {
            "message": "Vehicle is already parked.",
            "plate": plate,
            "slot_code": current_slot.slot_code if current_slot else slot_code,
        }

    # 3. Look up the slot — NO auto-creation ───────────────────────────────────
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_code == slot_code).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slot '{slot_code}' does not exist. Pre-configure it via the admin API.",
        )

    # 4. Guard slot already taken by a different vehicle ───────────────────────
    if slot.is_occupied:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slot '{slot_code}' is already occupied by another vehicle.",
        )

    # 5. Create parking record (uses FKs, not raw strings) ─────────────────────
    record = ParkingRecord(
        vehicle_id=vehicle.id,
        slot_id=slot.id,
        is_active=True,
    )
    db.add(record)

    # 6. Mark slot occupied ────────────────────────────────────────────────────
    slot.is_occupied = True

    db.commit()

    return {
        "message": "Vehicle parked successfully.",
        "plate": plate,
        "slot_code": slot_code,
    }


# ── Public service functions ───────────────────────────────────────────────────

def park_vehicle(db: Session, data: ParkVehicleRequest) -> dict:
    """
    Called by POST /ai/park.
    Used when the caller already has full vehicle data and wants to register it.
    """
    return _assign_vehicle_to_slot(
        db=db,
        plate=data.plate.upper(),
        slot_code=data.slot_code,
        color=data.color,
        vehicle_type=data.vehicle_type,
    )


def handle_slot_scan(db: Session, data: SlotScanResult) -> dict:
    """
    Called by POST /ai/scan-result.
    Handles both branches:
      - has_car=False → free the slot and close the parking record.
      - has_car=True  → assign the vehicle to the slot.
    """

    # ── Branch A: No car — free the slot ──────────────────────────────────
    if not data.has_car:
        slot = db.query(ParkingSlot).filter(
            ParkingSlot.slot_code == data.slot_code
        ).first()

        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Slot '{data.slot_code}' does not exist.",
            )

        if slot.is_occupied:
            active_record = (
                db.query(ParkingRecord)
                .filter(
                    ParkingRecord.slot_id == slot.id,
                    ParkingRecord.is_active == True,
                )
                .first()
            )
            if active_record:
                active_record.is_active = False
                active_record.exit_time = datetime.now(timezone.utc)

            slot.is_occupied = False
            db.commit()
            return {
                "message": "Slot freed — vehicle has exited.",
                "slot_code": data.slot_code,
                "has_car": False,
                "plate": None,
            }

        # Already free — no-op
        return {
            "message": "Slot already free. No change.",
            "slot_code": data.slot_code,
            "has_car": False,
            "plate": None,
        }

    # ── Branch B: Car present — assign it to the slot ─────────────────────
    # If plate is missing (OCR failed), generate a placeholder so the slot
    # still gets registered. The admin can correct it later via the dashboard.
    plate = data.plate if data.plate and data.plate.strip() else f"UNKNOWN-{data.slot_code}"

    result = _assign_vehicle_to_slot(
        db=db,
        plate=plate.upper(),
        slot_code=data.slot_code,
        color=data.color,
        vehicle_type=data.vehicle_type,
    )

    return {**result, "has_car": True}