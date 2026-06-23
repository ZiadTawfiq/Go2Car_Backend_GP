"""
Pydantic schemas for Vehicle.
"""
from typing import Optional, List
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
    owner_ids: List[int]

    model_config = {"from_attributes": True}



class VehicleLocationResponse(BaseModel):
    plate_number: str
    slot_code: int
    floor: int


# =========================================================
# ADVANCED SEARCH — REQUEST SCHEMA
# All fields are optional so any combination works,
# including no filters at all (returns all currently parked vehicles).
# Field `type` is the public-facing name; internally mapped to vehicle_type.
# =========================================================
class VehicleSearchRequest(BaseModel):
    plate_number: Optional[str] = None   # partial match via ILIKE
    color: Optional[str] = None          # partial match via ILIKE
    type: Optional[str] = None           # maps to Vehicle.vehicle_type
    floor: Optional[str] = None          # filters by Floor.floor_name
    section: Optional[str] = None        # filters by Section.section_name