from sqlalchemy.orm import Session
from app.models import ParkingSection
from app.schemas.parking_section import ParkingSectionOut
from typing import List

def get_all_sections(db: Session) -> List[ParkingSectionOut]:
    """Return all sections"""
    return db.query(ParkingSection).all()


def get_section_by_id(db: Session, section_id: int):
        return db.query(ParkingSection).filter(ParkingSection.id == section_id).first()