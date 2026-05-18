"""
Pydantic schemas for the AI integration endpoints.
"""
from typing import Optional
from pydantic import BaseModel


class ParkVehicleRequest(BaseModel):
    """
    Payload to manually register a detected vehicle into a slot.
    Sent when the caller already knows has_car=True and has the vehicle data.
    """
    plate: str
    slot_code: str
    color: Optional[str] = None
    vehicle_type: Optional[str] = None


class ParkVehicleResponse(BaseModel):
    """Response confirming the vehicle was stored and slot marked occupied."""
    message: str
    plate: str
    slot_code: str


# ── Scan result (sent by the external AI vision service) ──────────────────────

class SlotScanResult(BaseModel):
    """
    Payload sent by the external AI vision service after processing a camera snapshot.

    - has_car=False → backend frees the slot.
    - has_car=True  → backend registers the vehicle and marks slot occupied.
    """
    slot_code: str
    has_car: bool

    # Only present when has_car is True
    plate: Optional[str] = None
    color: Optional[str] = None
    vehicle_type: Optional[str] = None


class SlotScanResponse(BaseModel):
    """Response confirming what action the backend took after the scan."""
    message: str
    slot_code: str
    has_car: bool
    plate: Optional[str] = None