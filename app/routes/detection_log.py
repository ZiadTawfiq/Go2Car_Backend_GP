"""
Detection log routes — view detection log entries (admin).
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.detection_log import DetectionLogOut
from app.services import detection_log_service
from app.routes.dependencies import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/detection-logs", tags=["Detection Logs"])


@router.get("/", response_model=List[DetectionLogOut])
def all_detection_logs(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Return all detection logs, newest first. [JWT + admin]"""
    return detection_log_service.get_all_logs(db)


@router.get("/flagged", response_model=List[DetectionLogOut])
def flagged_detection_logs(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Return only flagged detection logs, newest first. [JWT + admin]"""
    return detection_log_service.get_flagged_logs(db)
