from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import Camera, ParkingSection
from app.schemas.camera import CameraOut 


def get_all_cameras(db: Session) -> List[CameraOut]:
    """Return every camera."""
    return db.query(Camera).options(
        joinedload(Camera.section).joinedload(ParkingSection.floor)
    ).all()


def get_active_cameras(db: Session) -> List[CameraOut]:
    """Return active cameras."""
    return db.query(Camera).options(
        joinedload(Camera.section).joinedload(ParkingSection.floor)
    ).filter(Camera.is_active == True).all()



def get_camera_by_id(db: Session, camera_id: int) -> Optional[CameraOut]:
    """Return a specific camera by its ID."""
    return db.query(Camera).options(
            joinedload(Camera.section).joinedload(ParkingSection.floor)
        ).filter(Camera.id == camera_id).first()