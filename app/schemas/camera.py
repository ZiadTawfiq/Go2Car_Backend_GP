from pydantic import BaseModel
from app.schemas.parking_section import ParkingSectionOut
from typing import Optional

class CameraOut(BaseModel):
    id: int
    name: str
    location_description: str
    is_active: bool
    section: ParkingSectionOut

    model_config = {"from_attributes": True}


class CameraCreate(BaseModel):
    name: str
    location_description: str
    section_id: int
    is_active: bool = True


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location_description: Optional[str] = None
    is_active: Optional[bool] = None


class CameraStats(BaseModel):
    total: int
    active: int
    inactive: int