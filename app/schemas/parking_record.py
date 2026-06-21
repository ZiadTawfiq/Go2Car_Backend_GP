"""
Pydantic schemas for ParkingRecord.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ParkingRecordOut(BaseModel):
    """Response schema for a parking record."""
    id: int
    plate_number: str
    slot_code: str
    floor: int
    entry_time: Optional[datetime]
    exit_time: Optional[datetime]
    is_active: bool
    image_path: Optional[str] = None

    model_config = {"from_attributes": True}


class VehicleExitRequest(BaseModel):
    """Request body to process a vehicle exit."""
    plate: str
