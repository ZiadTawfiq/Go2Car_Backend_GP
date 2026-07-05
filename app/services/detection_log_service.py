"""
Detection log service — query detection log entries.
"""
from typing import List

from sqlalchemy.orm import Session, joinedload

from app.models import DetectionLog


def _base_query(db: Session):
    """Shared base query with eager-loaded camera and slot."""
    return db.query(DetectionLog).options(
        joinedload(DetectionLog.camera),
        joinedload(DetectionLog.slot),
    )


def _serialize(log: DetectionLog) -> dict:
    return {
        "id": log.id,
        "camera_name": log.camera.name,
        "slot_code": log.slot.slot_code if log.slot else None,
        "slot_number": log.slot.slot_number if log.slot else None,
        "plate_number": log.plate_number,
        "vehicle_color": log.vehicle_color,
        "vehicle_type": log.vehicle_type,
        "detected_at": log.detected_at,
        "flagged_for_review": log.flagged_for_review,
    }


def get_all_logs(db: Session) -> List[dict]:
    """Return all detection logs, newest first."""
    logs = _base_query(db).order_by(DetectionLog.detected_at.desc()).all()
    return [_serialize(log) for log in logs]


def get_flagged_logs(db: Session) -> List[dict]:
    """Return only flagged detection logs, newest first."""
    logs = (
        _base_query(db)
        .filter(DetectionLog.flagged_for_review == True)
        .order_by(DetectionLog.detected_at.desc())
        .all()
    )
    return [_serialize(log) for log in logs]
