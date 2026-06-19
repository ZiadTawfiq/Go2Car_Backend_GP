from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.vehicle import Vehicle
from app.models.parking_record import ParkingRecord
from app.models.parking_slot import ParkingSlot
from app.schemas.vehicle import VehicleCreate
from app.utils import normalize_plate

import logging

logger = logging.getLogger(__name__)


# =========================================================
# HELPERS
# =========================================================
def validate_plate(plate: str):

    if not plate or plate.strip() == "":
        raise HTTPException(400, "Plate number is required")


# =========================================================
# CREATE VEHICLE
# =========================================================
def create_vehicle(
    db: Session,
    data: VehicleCreate,
    user_id: int
):

    plate = normalize_plate(data.plate_number)

    validate_plate(plate)

    existing = db.query(Vehicle).filter(
        Vehicle.plate_number == plate
    ).first()

    if existing:
        raise HTTPException(400, "Vehicle already exists")

    vehicle = Vehicle(
        plate_number=plate,
        color=data.color,
        vehicle_type=data.vehicle_type,
        owner_id=user_id
    )

    try:

        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)

        logger.info(f"Vehicle created: {plate}")

        return {
            "success": True,
            "data": vehicle
        }

    except SQLAlchemyError as e:

        db.rollback()

        logger.error(f"Create vehicle failed: {str(e)}")

        raise HTTPException(500, "Database error")


# =========================================================
# SEARCH BY PLATE (LOCATION)
# =========================================================
def search_by_plate(
    db: Session,
    plate: str
) -> dict:

    plate = normalize_plate(plate)

    validate_plate(plate)

    record = (
        db.query(ParkingRecord)
        .join(Vehicle, Vehicle.id == ParkingRecord.vehicle_id)
        .filter(
            Vehicle.plate_number == plate,
            ParkingRecord.is_active == True,
        )
        .first()
    )

    if not record:

        raise HTTPException(
            status_code=404,
            detail=f"No active parking record for '{plate}'"
        )

    return {
        "success": True,
        "data": {
            "plate_number": record.vehicle.plate_number,
            "slot": record.slot.slot_code,
            "section": record.slot.section.section_name,
            "floor": record.slot.section.floor.floor_name
        }
    }


# =========================================================
# SEARCH BY ATTRIBUTES
# =========================================================
def search_by_attributes(
    db: Session,
    color: Optional[str],
    vehicle_type: Optional[str]
):

    if not color and not vehicle_type:
        raise HTTPException(400, "Provide color or vehicle_type")

    query = (
        db.query(ParkingRecord)
        .join(Vehicle, Vehicle.id == ParkingRecord.vehicle_id)
        .filter(ParkingRecord.is_active == True)
    )

    if color:

        query = query.filter(
            Vehicle.color.ilike(f"%{color}%")
        )

    if vehicle_type:

        query = query.filter(
            Vehicle.vehicle_type.ilike(f"%{vehicle_type}%")
        )

    records = query.all()

    if not records:
        raise HTTPException(404, "No vehicles found")

    results = [
        {
            "plate_number": r.vehicle.plate_number,
            "slot": r.slot.slot_code,
            "section": r.slot.section.section_name,
            "floor": r.slot.section.floor.floor_name,
            "entry_time": r.entry_time,
            "is_active": r.is_active
        }
        for r in records
    ]

    return {
        "success": True,
        "count": len(results),
        "data": results
    }


# =========================================================
# EXIT VEHICLE
# =========================================================
def exit_vehicle(
    db: Session,
    plate: str
) -> dict:

    plate = normalize_plate(plate)

    validate_plate(plate)

    record = (
        db.query(ParkingRecord)
        .join(Vehicle, Vehicle.id == ParkingRecord.vehicle_id)
        .filter(
            Vehicle.plate_number == plate,
            ParkingRecord.is_active == True,
        )
        .first()
    )

    if not record:
        raise HTTPException(404, "No active parking session")

    try:

        record.is_active = False
        record.exit_time = datetime.now(timezone.utc)

        if record.slot:
            record.slot.is_occupied = False

        db.commit()

        logger.info(f"Vehicle exited: {plate}")

        return {
            "success": True,
            "message": f"Vehicle '{plate}' exited successfully"
        }

    except SQLAlchemyError as e:

        db.rollback()

        logger.error(f"Exit vehicle failed: {str(e)}")

        raise HTTPException(500, "Database error")


# =========================================================
# FUZZY SEARCH
# =========================================================
def fuzzy_search(
    db: Session,
    plate: str
):

    plate = normalize_plate(plate)

    results = (
        db.query(Vehicle)
        .filter(
            Vehicle.plate_number.ilike(f"%{plate}%")
        )
        .all()
    )

    if not results:
        raise HTTPException(404, "No matching vehicles")

    return {
        "success": True,
        "data": [
            v.plate_number for v in results
        ]
    }


# =========================================================
# GET USER VEHICLES
# =========================================================
def get_user_vehicles(
    db: Session,
    user_id: int
):

    vehicles = db.query(Vehicle).filter(
        Vehicle.owner_id == user_id
    ).all()

    return {
        "success": True,
        "count": len(vehicles),
        "data": [
            {
                "plate_number": v.plate_number,
                "color": v.color,
                "vehicle_type": v.vehicle_type
            }
            for v in vehicles
        ]
    }


# =========================================================
# GET VEHICLE MAP
# =========================================================
def get_vehicle_map(
    db: Session,
    plate: str
):

    plate = normalize_plate(plate)

    validate_plate(plate)

    record = (
        db.query(ParkingRecord)
        .join(Vehicle, Vehicle.id == ParkingRecord.vehicle_id)
        .filter(
            Vehicle.plate_number == plate,
            ParkingRecord.is_active == True
        )
        .first()
    )

    if not record:
        raise HTTPException(404, "Vehicle not found")

    floor_code = record.slot.section.floor.floor_code

    return {
        "success": True,
        "data": {
            "map_path": f"/static/maps/{floor_code}.png",
            "slot": record.slot.slot_code,
            "section": record.slot.section.section_name,
            "floor": record.slot.section.floor.floor_name
        }
    }


# =========================================================
# VEHICLE HISTORY
# =========================================================
def get_vehicle_history(
    db: Session,
    plate: Optional[str] = None,
    user_id: Optional[int] = None
):

    query = (
        db.query(ParkingRecord)
        .join(Vehicle, Vehicle.id == ParkingRecord.vehicle_id)
    )

    if user_id is not None:
        query = query.filter(Vehicle.owner_id == user_id)

    if plate:

        plate = normalize_plate(plate)

        query = query.filter(
            Vehicle.plate_number == plate
        )

    records = query.order_by(
        ParkingRecord.entry_time.desc()
    ).all()

    if not records:
        raise HTTPException(404, "No history found")

    return {
        "success": True,
        "count": len(records),
        "data": [
            {
                "plate_number": r.vehicle.plate_number,
                "slot": r.slot.slot_code,
                "section": r.slot.section.section_name,
                "floor": r.slot.section.floor.floor_name,
                "entry_time": r.entry_time,
                "exit_time": r.exit_time,
                "is_active": r.is_active
            }
            for r in records
        ]
    }