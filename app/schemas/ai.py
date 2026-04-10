"""
Pydantic schema for the AI detection endpoint.
"""
from typing import Optional
from pydantic import BaseModel


class AIDetectRequest(BaseModel):
    """
    Payload sent by the AI module when it detects a vehicle.
    The AI sends plate number, assigned slot, and optional vehicle attributes.
    """
    plate: str
    slot_code: str
    floor: int
    color: Optional[str] = None
    type: Optional[str] = None


class AIDetectResponse(BaseModel):
    """Response confirming what the backend stored."""
    message: str
    plate: str
    slot_code: str
    floor: int
