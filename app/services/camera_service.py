from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
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


def create_camera(db: Session, camera_data):
    new_camera = Camera(
        name=camera_data.name,
        location_description=camera_data.location_description,
        section_id=camera_data.section_id,
        is_active=camera_data.is_active
    )

    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)

    return new_camera


def update_camera(db: Session, camera_id: int, camera_data):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()

    if not camera:
        return None

    update_data = camera_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(camera, key, value)

    db.commit()
    db.refresh(camera)

    return camera



def get_camera_stats(db: Session):
    result = db.query(
        func.count(Camera.id).label("total"),
        func.sum(case((Camera.is_active == True, 1), else_=0)).label("active"),
        func.sum(case((Camera.is_active == False, 1), else_=0)).label("inactive"),
    ).one()

    return {
        "total": result.total or 0,
        "active": result.active or 0,
        "inactive": result.inactive or 0
    }