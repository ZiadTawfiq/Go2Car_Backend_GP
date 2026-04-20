from sqlalchemy.orm import Session
from app.models import ParkingFloor
from app.schemas.parking_floor import ParkingFloorOut
from typing import List

def get_all_floors(db: Session) -> List[ParkingFloorOut]:
    """Return all floors"""
    return db.query(ParkingFloor).all()