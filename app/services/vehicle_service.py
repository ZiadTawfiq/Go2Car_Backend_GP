from sqlalchemy.orm import mapper
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import case, func, or_

from app.models.vehicle import Vehicle
from app.models.parking_record import ParkingRecord
from app.models.parking_slot import ParkingSlot
from app.models.parking_section import ParkingSection                
from app.models.parking_floor import ParkingFloor                     
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
    from app.models.user import User

    plate = normalize_plate(data.plate_number)

    validate_plate(plate)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    existing = db.query(Vehicle).filter(
        Vehicle.plate_number == plate
    ).first()

    if existing:
        if user in existing.owners:
            raise HTTPException(400, "Vehicle already registered to you")
        
        # Add user as an owner to the existing vehicle
        existing.owners.append(user)
        try:
            db.commit()
            logger.info(f"User {user_id} added to vehicle {plate}")
            return {
                "success": True,
                "message": f"Added as an owner of vehicle '{plate}'",
                "data": existing
            }
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to add owner to vehicle: {str(e)}")
            raise HTTPException(500, "Database error")

    vehicle = Vehicle(
        plate_number=plate,
        color=data.color,
        vehicle_type=data.vehicle_type
    )
    vehicle.owners.append(user)

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

    records = (
        db.query(ParkingRecord)
        .join(Vehicle, Vehicle.id == ParkingRecord.vehicle_id)
        .filter(
            Vehicle.plate_number.ilike(f"%{plate}%"),
            ParkingRecord.is_active == True,
        )
        .all()
    )

    if not records:

        raise HTTPException(
            status_code=404,
            detail=f"No active parking record found for '{plate}'"
        )

    return {
        "success": True,
        "count": len(records),
        "data": [
            {
                "plate_number": record.vehicle.plate_number,
                "vehicle_color": record.vehicle.color,
                "vehicle_type": record.vehicle.vehicle_type,
                "slot": record.slot.slot_code,
                "slot_number": record.slot.slot_number,
                "section": record.slot.section.section_name,
                "section_display": record.slot.section.section_display,
                "section_name_display": record.slot.section.section_name_display,
                "floor": record.slot.section.floor.floor_name,
                "image_path": record.image_path
            } for record in records
        ]
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
            "vehicle_color": r.vehicle.color,
            "vehicle_type": r.vehicle.vehicle_type,
            "slot": r.slot.slot_code,
            "slot_number": r.slot.slot_number,
            "section": r.slot.section.section_name,
            "section_display": r.slot.section.section_display,
            "section_name_display": r.slot.section.section_name_display,
            "floor": r.slot.section.floor.floor_name,
            "entry_time": r.entry_time,
            "is_active": r.is_active,
            "image_path": r.image_path
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
    from app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    vehicles = user.vehicles

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

    full_section_code = record.slot.section.section_code
    # Use the full section_code as-is (e.g. "F1_A2") — files are named F1_A2.png

    import os
    from pathlib import Path
    # Use absolute path relative to project root (works regardless of Railway CWD)
    project_root = Path(__file__).resolve().parent.parent.parent
    maps_dir = project_root / "static" / "maps"
    map_file = maps_dir / f"{full_section_code}.png"

    if map_file.exists():
        map_path = f"/static/maps/{full_section_code}.png"
    else:
        # Fallback — return section path anyway (static server will 404 if missing)
        map_path = f"/static/maps/{full_section_code}.png"

    return {
        "success": True,
        "data": {
            "map_path": map_path,
            "slot": record.slot.slot_code,
            "slot_number": record.slot.slot_number,
            "section": record.slot.section.section_name,
            "section_display": record.slot.section.section_display,
            "section_name_display": record.slot.section.section_name_display,
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
    from app.models.user import User

    query = (
        db.query(ParkingRecord)
        .join(Vehicle, Vehicle.id == ParkingRecord.vehicle_id)
    )

    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(404, "User not found")
        
        if plate:
            plate = normalize_plate(plate)
            vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
            if not vehicle:
                raise HTTPException(404, f"Vehicle '{plate}' not found")
            
            # Check ownership
            if user_id not in [o.id for o in vehicle.owners]:
                raise HTTPException(403, "You do not own this vehicle")
                
            query = query.filter(Vehicle.id == vehicle.id)
        else:
            vehicle_ids = [v.id for v in user.vehicles]
            if not vehicle_ids:
                raise HTTPException(404, "No history found")
            query = query.filter(Vehicle.id.in_(vehicle_ids))
    else:
        if plate:
            plate = normalize_plate(plate)
            query = query.filter(Vehicle.plate_number == plate)

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
                "slot_number": r.slot.slot_number,
                "section": r.slot.section.section_name,
                "section_display": r.slot.section.section_display,
                "section_name_display": r.slot.section.section_name_display,
                "floor": r.slot.section.floor.floor_name,
                "entry_time": r.entry_time,
                "exit_time": r.exit_time,
                "is_active": r.is_active,
                "image_path": r.image_path
            }
            for r in records
        ]
    }

# =========================================================
# UPDATE MY VEHICLE
# =========================================================
def update_vehicle(
    db: Session,
    plate: str,
    color: Optional[str],
    vehicle_type: Optional[str],
    user_id: int
):
    plate = normalize_plate(plate)
    validate_plate(plate)

    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if not vehicle:
        raise HTTPException(404, f"Vehicle '{plate}' not found")

    if user_id not in [o.id for o in vehicle.owners]:
        raise HTTPException(403, "You do not own this vehicle")

    if not color and not vehicle_type:
        raise HTTPException(400, "Provide at least one field to update (color or vehicle_type)")

    if color:
        vehicle.color = color
    if vehicle_type:
        vehicle.vehicle_type = vehicle_type

    try:
        db.commit()
        db.refresh(vehicle)
        logger.info(f"Vehicle updated: {plate} by user {user_id}")
        return {
            "success": True,
            "message": f"Vehicle '{plate}' updated",
            "data": {
                "plate_number": vehicle.plate_number,
                "color": vehicle.color,
                "vehicle_type": vehicle.vehicle_type
            }
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Update vehicle failed: {str(e)}")
        raise HTTPException(500, "Database error")


# =========================================================
# DELETE MY VEHICLE (remove ownership)
# =========================================================
def delete_vehicle(
    db: Session,
    plate: str,
    user_id: int
):
    from app.models.user import User

    plate = normalize_plate(plate)
    validate_plate(plate)

    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if not vehicle:
        raise HTTPException(404, f"Vehicle '{plate}' not found")

    if user_id not in [o.id for o in vehicle.owners]:
        raise HTTPException(403, "You do not own this vehicle")

    # Block deletion if vehicle is currently parked
    active_record = (
        db.query(ParkingRecord)
        .filter(
            ParkingRecord.vehicle_id == vehicle.id,
            ParkingRecord.is_active == True
        )
        .first()
    )
    if active_record:
        raise HTTPException(
            400,
            "Cannot remove vehicle while it has an active parking session"
        )

    user = db.query(User).filter(User.id == user_id).first()

    try:
        vehicle.owners.remove(user)

        # If no owners remain, delete the vehicle entirely
        if not vehicle.owners:
            db.delete(vehicle)
            msg = f"Vehicle '{plate}' fully deleted (no remaining owners)"
        else:
            msg = f"You have been removed as an owner of '{plate}'"

        db.commit()
        logger.info(f"Vehicle delete/disown: {plate} by user {user_id}")
        return {"success": True, "message": msg}

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Delete vehicle failed: {str(e)}")
        raise HTTPException(500, "Database error")
    

# =========================================================
# ADVANCED SEARCH
# =========================================================
def advanced_search(
    db: Session,
    plate_number: Optional[str],
    color: Optional[str],
    vehicle_type: Optional[str],
    floor: Optional[str],
    section: Optional[str],
):

    query = (
        db.query(ParkingRecord)
        .join(Vehicle, Vehicle.id == ParkingRecord.vehicle_id)
        .join(ParkingSlot, ParkingSlot.id == ParkingRecord.slot_id)
        .join(ParkingSection, ParkingSection.id == ParkingSlot.section_id)
        .join(ParkingFloor, ParkingFloor.id == ParkingSection.floor_id)
        .filter(ParkingRecord.is_active == True)
    )

    # ── Conditional filters (most selective → least selective) ────────────────

    # 1. Floor
    if floor:
        query = query.filter(ParkingFloor.floor_name.ilike(f"%{floor}%"))

    # 2. Section
    if section:
        query = query.filter(ParkingSection.section_name.ilike(f"%{section}%"))

    # 3. Plate — substring match OR fuzzy trigram similarity, ranked best-first
    plate_similarity = None
    if plate_number:
        normalized = normalize_plate(plate_number)
        plate_similarity = func.similarity(Vehicle.plate_number, normalized)

        query = query.filter(
            or_(
                Vehicle.plate_number.ilike(f"%{normalized}%"),  # your original exact-substring rule
                plate_similarity > 0.3,                          # catches typos e.g. ABD123 -> ABC123
            )
        )

    # 4. Color
    if color:
        query = query.filter(Vehicle.color.ilike(f"%{color}%"))

    # 5. Vehicle type
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type.ilike(f"%{vehicle_type}%"))

    # ── Ranking ─────────────────────────────────────────────────────────────
    # Exact match first, then "starts with", then substring, then fuzzy matches
    # ordered by similarity score.
    if plate_number:
        query = query.order_by(
            case(
                (Vehicle.plate_number == normalized, 0),
                (Vehicle.plate_number.ilike(f"{normalized}%"), 1),
                (Vehicle.plate_number.ilike(f"%{normalized}%"), 2),
                else_=3,
            ),
            plate_similarity.desc(),
        )

    # ── Execute ───────────────────────────────────────────────────────────────
    records = query.all()

    if not records:
        raise HTTPException(404, "No vehicles found matching the given filters")

    # ── Serialize ─────────────────────────────────────────────────────────────
    data = [
        {
            "id": r.vehicle.id,
            "plate_number": r.vehicle.plate_number,
            "color": r.vehicle.color,
            "type": r.vehicle.vehicle_type,
            "slot": r.slot.slot_code,
            "slot_number": r.slot.slot_number,
            "section": r.slot.section.section_name,
            "section_display": r.slot.section.section_display,
            "section_name_display": r.slot.section.section_name_display,
            "floor": r.slot.section.floor.floor_name,
            "image_path": r.image_path,
        }
        for r in records
    ]

    return {
        "success": True,
        "count": len(data),
        "data": data,
    }