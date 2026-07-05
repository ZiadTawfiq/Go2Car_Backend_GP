"""
Pydantic schemas for ParkingSection.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.parking_floor import ParkingFloorOut

class ParkingSectionOut(BaseModel):
    id: int
    section_code: str
    section_name: str
    section_display: str
    section_name_display: str
    floor: ParkingFloorOut

    model_config = {"from_attributes": True}
