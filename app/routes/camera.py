from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.camera import CameraOut
from app.services import camera_service

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("/all", response_model=list[CameraOut])
def all_cameras(db: Session = Depends(get_db)):
    return camera_service.get_all_cameras(db)