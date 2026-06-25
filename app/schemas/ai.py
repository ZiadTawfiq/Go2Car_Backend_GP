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
    image_path: Optional[str] = None


class ParkVehicleResponse(BaseModel):
    """Response confirming the vehicle was stored and slot marked occupied."""
    message: str
    plate: str
    slot_code: str


# ── Scan result (sent by the external AI vision service) ──────────────────────

class SlotScanResult(BaseModel):
    # AI field names → backend maps them internally
    event_type: str                        # "arrival" or "departure"
    camera_id: Optional[str] = None
    slot_id: str                           # this is your slot_code
    section: Optional[str] = None

    # Arrival fields
    plate_text: Optional[str] = None      # maps to → plate
    plate_confidence: Optional[float] = None
    color: Optional[str] = None
    color_confidence: Optional[float] = None
    car_type: Optional[str] = None        # maps to → vehicle_type
    car_type_confidence: Optional[float] = None
    image_path: Optional[str] = None
    image_base64: Optional[str] = None

    # Departure fields
    duration_minutes: Optional[float] = None

    # Computed properties for internal use
    @property
    def slot_code(self) -> str:
        return self.slot_id

    @property
    def has_car(self) -> bool:
        return self.event_type == "arrival"

    @property
    def plate(self) -> Optional[str]:
        return self.plate_text

    @property
    def vehicle_type(self) -> Optional[str]:
        return self.car_type


class SlotScanResponse(BaseModel):
    """Response confirming what action the backend took after the scan."""
    message: str
    slot_code: str
    has_car: bool
    plate: Optional[str] = None