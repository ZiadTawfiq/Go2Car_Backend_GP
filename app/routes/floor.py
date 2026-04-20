from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.parking_floor import ParkingFloorOut
from app.services import floor_service
from app.db.database import get_db

router = APIRouter(prefix="/floors", tags=["Floors"])

@router.get("/all", response_model=list[ParkingFloorOut])
def get_floors(db: Session = Depends(get_db)):
    return floor_service.get_all_floors(db)


@router.get("/{floor_id}", response_model=ParkingFloorOut)
def get_floor_by_id(floor_id: int, db: Session = Depends(get_db)):
    floor = floor_service.get_floor_by_id(db, floor_id)

    if not floor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Floor not found"
        )

    return floor
    