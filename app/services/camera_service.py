from typing import List

from sqlalchemy.orm import Session, joinedload

from app.models import Camera, ParkingSection
from app.schemas.camera import CameraOut 


def get_all_cameras(db: Session) -> List[CameraOut]:
    """Return every camera."""
    return db.query(Camera).options(
        joinedload(Camera.section).joinedload(ParkingSection.floor)
    ).all()