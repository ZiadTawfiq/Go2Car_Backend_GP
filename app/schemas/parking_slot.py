"""
Pydantic schemas for ParkingSlot.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ParkingSlotCreate(BaseModel):
    """Used by admin to create a new slot."""
    slot_code: str
    section_id: int


class ParkingSlotOut(BaseModel):
    """Response schema for a parking slot."""
    id: int
    slot_code: str
    section_id: int
    is_occupied: bool
    last_updated: Optional[datetime]

    model_config = {"from_attributes": True}
