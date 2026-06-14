from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.camera import CameraOut, CameraCreate, CameraUpdate, CameraStats
from app.services import camera_service
from app.routes.dependencies import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("/all", response_model=list[CameraOut])
def all_cameras(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    return camera_service.get_all_cameras(db)


@router.get("/active", response_model=list[CameraOut])
def active_cameras(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    return camera_service.get_active_cameras(db)


@router.get("/stats", response_model=CameraStats)
def camera_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    return camera_service.get_camera_stats(db)


@router.get("/{camera_id}", response_model=CameraOut)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    """Return one Camera."""
    camera = camera_service.get_camera_by_id(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.post("/", response_model=CameraOut)
def create_camera_endpoint(
    camera: CameraCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    return camera_service.create_camera(db, camera)


@router.patch("/{camera_id}", response_model=CameraOut)
def update_camera_endpoint(
    camera_id: int,
    camera: CameraUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    updated_camera = camera_service.update_camera(db, camera_id, camera)
    if not updated_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return updated_camera