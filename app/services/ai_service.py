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
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.vehicle import Vehicle
from app.models.parking_slot import ParkingSlot
from app.models.parking_record import ParkingRecord
from app.models.detection_log import DetectionLog
from app.schemas.ai import ParkVehicleRequest, SlotScanResult

logger = logging.getLogger(__name__)


# ── Detection logging ─────────────────────────────────────────────────────────

def _create_detection_log(
    db: Session,
    camera_id: int,
    slot_code: str | None,
    plate_number: str | None,
    vehicle_color: str | None,
    vehicle_type: str | None,
    event_type: str | None,
) -> None:
    """
    Insert a raw detection record into detection_logs immediately upon receiving
    a scan-result payload.  Isolated from the main business flow — any failure
    here is caught and logged so it never interrupts parking processing.

    Field mapping from AI payload:
        camera_id      → camera_id     (FK → cameras.id)
        slot_code      → resolved to   slot_id (FK → parking_slots.id), nullable
        plate_text     → plate_number
        color          → vehicle_color
        car_type       → vehicle_type
        event_type     → event_type    (stored as-is for admin review workflows)
    """
    try:
        # Resolve slot_code → slot_id (nullable: unknown codes are stored as NULL
        # rather than raising — logging must never block the main flow).
        slot_id: int | None = None
        if slot_code:
            slot = (
                db.query(ParkingSlot)
                .filter(ParkingSlot.slot_code == slot_code)
                .first()
            )
            slot_id = slot.id if slot else None

        log_entry = DetectionLog(
            camera_id=camera_id,
            slot_id=slot_id,
            plate_number=plate_number or None,
            vehicle_color=vehicle_color or None,
            vehicle_type=vehicle_type or None,
            flagged_for_review=(bool(event_type and event_type.startswith("error:"))),
        )
        db.add(log_entry)
        db.flush()   # write within the current transaction; caller commits later
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Detection log creation failed — skipping (camera_id=%s, slot=%s): %s",
            camera_id,
            slot_code,
            exc,
        )
        db.rollback()


# ── Shared internal helper ─────────────────────────────────────────────────────

def _assign_vehicle_to_slot(
    db: Session,
    plate: str,
    slot_code: str,
    color: str | None,
    vehicle_type: str | None,
    image_path: str | None = None,
) -> dict:
    """
    Core pipeline: upsert vehicle → guard duplicates → link to slot → create record.
    Supports updating the plate text for occupied slots (LPR refinement).
    """
    # 1. Look up the slot first
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_code == slot_code).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slot '{slot_code}' does not exist. Pre-configure it via the admin API.",
        )

    # 2. Look up or create vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if not vehicle:
        vehicle = Vehicle(
            plate_number=plate,
            color=color,
            vehicle_type=vehicle_type,
        )
        db.add(vehicle)
        db.flush()
    else:
        # Enrich existing record if new info is available
        if color and not vehicle.color:
            vehicle.color = color
        if vehicle_type and not vehicle.vehicle_type:
            vehicle.vehicle_type = vehicle_type

    # 3. If slot is occupied, handle potential update/refinement of the plate
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
            current_vehicle = db.query(Vehicle).filter(Vehicle.id == active_record.vehicle_id).first()
            if current_vehicle:
                if current_vehicle.plate_number != plate:
                    # Update the active record's vehicle to the refined one
                    active_record.vehicle_id = vehicle.id
                    db.commit()
                    return {
                        "message": f"Updated slot '{slot_code}' vehicle plate from '{current_vehicle.plate_number}' to '{plate}'.",
                        "plate": plate,
                        "slot_code": slot_code,
                    }
                else:
                    # Same plate, idempotent
                    db.commit()
                    return {
                        "message": "Vehicle is already parked.",
                        "plate": plate,
                        "slot_code": slot_code,
                    }

    # 4. Guard duplicate active session (if vehicle is already parked in ANOTHER slot)
    active_record = (
        db.query(ParkingRecord)
        .filter(
            ParkingRecord.vehicle_id == vehicle.id,
            ParkingRecord.is_active == True,
        )
        .first()
    )
    if active_record:
        db.commit()
        current_slot = db.query(ParkingSlot).filter(
            ParkingSlot.id == active_record.slot_id
        ).first()
        return {
            "message": "Vehicle is already parked.",
            "plate": plate,
            "slot_code": current_slot.slot_code if current_slot else slot_code,
        }

    # 5. Create parking record
    record = ParkingRecord(
        vehicle_id=vehicle.id,
        slot_id=slot.id,
        is_active=True,
        image_path=image_path,
    )
    db.add(record)

    # 6. Mark slot occupied
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
        image_path=data.image_path,
    )


def handle_slot_scan(db: Session, data: SlotScanResult) -> dict:
    """
    Called by POST /ai/scan-result.
    Handles both branches:
      - has_car=False → free the slot and close the parking record.
      - has_car=True  → assign the vehicle to the slot.
    """

    # ── Detection log — fire before any business logic ─────────────────────
    # Captures every inbound scan unconditionally so the detection_logs table
    # reflects the raw stream from the AI edge node, independent of outcome.
    _create_detection_log(
        db=db,
        camera_id=data.camera_id,
        slot_code=data.slot_code,
        plate_number=data.plate,
        vehicle_color=data.color,
        vehicle_type=data.vehicle_type,
        event_type=data.event_type,
    )

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
        image_path=data.image_path,
    )

    return {**result, "has_car": True}