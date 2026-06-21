"""
Pydantic schemas for Reservation.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.reservation import ReservationStatus


class ReservationCreate(BaseModel):
    slot_code: str
    plate_number: str
    start_time: datetime
    end_time: datetime


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    slot_id: int
    vehicle_id: Optional[int]
    start_time: datetime
    end_time: datetime
    status: ReservationStatus
    created_at: datetime

    model_config = {"from_attributes": True}
