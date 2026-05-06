"""
Pydantic schemas for Vehicle.
"""
from typing import Optional
from pydantic import BaseModel


class VehicleCreate(BaseModel):
    plate_number: str
    color: Optional[str] = None
    vehicle_type: Optional[str] = None


class VehicleResponse(BaseModel):
    id: int
    plate_number: str
    color: Optional[str]
    vehicle_type: Optional[str]
    owner_id: Optional[int]

    model_config = {"from_attributes": True}


class VehicleLocationResponse(BaseModel):
    plate_number: str
    slot_code: int
    floor: int