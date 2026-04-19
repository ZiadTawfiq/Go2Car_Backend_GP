"""
Pydantic schemas for ParkingFloor.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ParkingFloorOut(BaseModel):
    id: int
    floor_code: str
    floor_name: str

    model_config = {"from_attributes": True}