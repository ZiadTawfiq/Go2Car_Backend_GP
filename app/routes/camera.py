from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.camera import CameraOut
from app.services import camera_service

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("/all", response_model=list[CameraOut])
def all_cameras(db: Session = Depends(get_db)):
    return camera_service.get_all_cameras(db)


@router.get("/active", response_model=list[CameraOut])
def active_cameras(db: Session = Depends(get_db)):
    return camera_service.get_active_cameras(db)


@router.get("/{camera_id}", response_model=CameraOut)
def get_camera(camera_id: int,db: Session = Depends(get_db)):
    """Return one Camera."""
    camera = camera_service.get_camera_by_id(db,camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera