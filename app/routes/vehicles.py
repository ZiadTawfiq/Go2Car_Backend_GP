from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.vehicle import VehicleCreate
from app.services.vehicle_service import (
    create_vehicle,
    search_by_plate,
    search_by_attributes,
    exit_vehicle,
    fuzzy_search,
    get_user_vehicles,
    get_vehicle_map,
    get_vehicle_history
)

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)


# ---------------------------
# CREATE VEHICLE
# ---------------------------
@router.post(
    "/",
    summary="Create vehicle",
    description="Register a new vehicle"
)
def create(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    return create_vehicle(db, data, user_id)


# ---------------------------
# FUZZY SEARCH
# ---------------------------
@router.get(
    "/search",
    summary="Fuzzy search vehicle",
    description="Search vehicle by partial plate number"
)
def search(
    plate: str,
    db: Session = Depends(get_db)
):
    return fuzzy_search(db, plate)


# ---------------------------
# SEARCH BY ATTRIBUTES
# ---------------------------
@router.get(
    "/search/attributes",
    summary="Search by attributes",
    description="Search vehicles by color or vehicle type"
)
def search_attributes(
    color: Optional[str] = Query(None),
    vehicle_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return search_by_attributes(db, color, vehicle_type)


# ---------------------------
# VEHICLE HISTORY
# ---------------------------
@router.get(
    "/history",
    summary="View vehicle history",
    description="Admin endpoint to view parking history"
)
def history(
    plate: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return get_vehicle_history(db, plate)


# ---------------------------
# GET USER VEHICLES
# ---------------------------
@router.get(
    "/user/me",
    summary="Get my vehicles",
    description="Get vehicles owned by current user"
)
def my_vehicles(
    db: Session = Depends(get_db),
    user_id: int = 1
):
    return get_user_vehicles(db, user_id)


# ---------------------------
# GET VEHICLE LOCATION
# ---------------------------
@router.get(
    "/{plate}/location",
    summary="Get vehicle location",
    description="Get slot and floor for a vehicle"
)
def get_location(
    plate: str,
    db: Session = Depends(get_db)
):
    return search_by_plate(db, plate)


# ---------------------------
# GET VEHICLE MAP
# ---------------------------
@router.get(
    "/{plate}/map",
    summary="Get vehicle map",
    description="Get map path for vehicle location"
)
def get_map(
    plate: str,
    db: Session = Depends(get_db)
):
    return get_vehicle_map(db, plate)


# ---------------------------
# EXIT VEHICLE
# ---------------------------
@router.post(
    "/{plate}/exit",
    summary="Exit vehicle",
    description="Mark vehicle as exited and free parking slot"
)
def exit(
    plate: str,
    db: Session = Depends(get_db)
):
    return exit_vehicle(db, plate)