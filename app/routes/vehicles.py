"""
Vehicle routes — search by plate, search by attributes, vehicle exit.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.vehicle import VehicleLocation
from app.schemas.parking_record import VehicleExitRequest
from app.services import vehicle_service

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("/search", response_model=VehicleLocation)
def search_by_plate(
    plate: str = Query(..., description="License plate number to search for"),
    db: Session = Depends(get_db),
):
    """
    🔍 Primary search — find where a vehicle is currently parked by plate number.
    Returns slot_code and floor number.
    """
    return vehicle_service.search_by_plate(db, plate)


@router.get("/search-by-attributes", response_model=List[VehicleLocation])
def search_by_attributes(
    color: Optional[str] = Query(None, description="Vehicle color (e.g. white, red)"),
    type: Optional[str] = Query(None, description="Vehicle type (e.g. sedan, SUV)"),
    db: Session = Depends(get_db),
):
    """
    🔍 Fallback search — find parked vehicles by color and/or type.
    Useful when the user doesn't know their exact plate number.
    """
    return vehicle_service.search_by_attributes(db, color, type)


@router.post("/exit")
def exit_vehicle(data: VehicleExitRequest, db: Session = Depends(get_db)):
    """
    🚗 Process a vehicle exit:
    closes the parking record, sets exit_time, and frees the slot.
    """
    return vehicle_service.exit_vehicle(db, data.plate)
