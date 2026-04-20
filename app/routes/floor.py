from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.parking_floor import ParkingFloorOut
from app.services import floor_service
from app.db.database import get_db

router = APIRouter(prefix="/floors", tags=["Floors"])

@router.get("/all", response_model=list[ParkingFloorOut])
def get_floors(db: Session = Depends(get_db)):
    return floor_service.get_all_floors(db)
    