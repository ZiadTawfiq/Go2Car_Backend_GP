from fastapi import APIRouter, Depends, Query, HTTPException, status
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
from app.routes.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)


# ---------------------------
# CREATE VEHICLE  [JWT required]
# ---------------------------
@router.post(
    "/",
    summary="Create vehicle",
    description="Register a new vehicle"
)
def create(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_vehicle(db, data, current_user.id)


# ---------------------------
# FUZZY SEARCH  [public]
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
# SEARCH BY ATTRIBUTES  [public]
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
# VEHICLE HISTORY  [JWT — own vehicles only]
# ---------------------------
@router.get(
    "/history",
    summary="View vehicle history",
    description="Returns parking history for the current user's vehicles"
)
def history(
    plate: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_vehicle_history(db, plate, current_user.id)


# ---------------------------
# GET USER VEHICLES  [JWT required]
# ---------------------------
@router.get(
    "/user/me",
    summary="Get my vehicles",
    description="Get vehicles owned by current user"
)
def my_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_vehicles(db, current_user.id)


# ---------------------------
# SEARCH BY PLATE  [JWT required]
# ---------------------------
@router.get(
    "/search/plate",
    summary="Search by plate",
    description="Find exactly where a vehicle is parked by plate number"
)
def search_plate(
    plate: str = Query(..., description="License plate number to search for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return search_by_plate(db, plate)


# ---------------------------
# GET VEHICLE MAP  [JWT required]
# ---------------------------
@router.get(
    "/{plate}/map",
    summary="Get vehicle map",
    description="Get map path for vehicle location"
)
def get_map(
    plate: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_vehicle_map(db, plate)


# ---------------------------
# EXIT VEHICLE  [JWT + admin only]
# ---------------------------
@router.post(
    "/{plate}/exit",
    summary="Exit vehicle",
    description="Mark vehicle as exited and free parking slot"
)
def exit_vehicle_route(
    plate: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return exit_vehicle(db, plate)