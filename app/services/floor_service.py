from sqlalchemy.orm import Session
from app.models import ParkingFloor
from app.schemas.parking_floor import ParkingFloorOut
from typing import List

def get_all_floors(db: Session) -> List[ParkingFloorOut]:
    """Return all floors"""
    return db.query(ParkingFloor).all()


def get_floor_by_id(db: Session, floor_id: int):
        return db.query(ParkingFloor).filter(ParkingFloor.id == floor_id).first()