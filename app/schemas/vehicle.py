"""
Pydantic schemas for Vehicle.
"""
from typing import Optional
from pydantic import BaseModel


class VehicleCreate(BaseModel):
    """Used internally when AI creates a vehicle."""
    plate_number: str
    color: Optional[str] = None
    type: Optional[str] = None
    owner_id: Optional[int] = None


class VehicleOut(BaseModel):
    """Response schema for a vehicle."""
    id: int
    plate_number: str
    color: Optional[str]
    type: Optional[str]
    owner_id: Optional[int]

    model_config = {"from_attributes": True}


class VehicleLocation(BaseModel):
    """Response when a user searches for their car."""
    plate_number: str
    slot_code: str
    floor: int
