"""
Pydantic schemas for DetectionLog.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class DetectionLogOut(BaseModel):
    """Response schema for a detection log entry."""
    id: int
    camera_name: str
    slot_code: Optional[str] = None
    plate_number: Optional[str] = None
    vehicle_color: Optional[str] = None
    vehicle_type: Optional[str] = None
    detected_at: Optional[datetime] = None
    flagged_for_review: bool

    model_config = {"from_attributes": True}

