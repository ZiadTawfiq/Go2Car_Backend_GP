"""
AI integration routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.ai import (
    SlotScanResult,
    SlotScanResponse,
)
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["AI Integration"])


@router.post("/scan-result", response_model=SlotScanResponse)
def scan_result(data: SlotScanResult, db: Session = Depends(get_db)):
    """
    📸 Called by the external AI vision service after processing a camera snapshot.

    The AI service sends:
      - slot_code        : which slot was scanned
      - has_car          : True / False
      - plate/color/vehicle_type : present only when has_car is True

    Backend either frees the slot (has_car=False) or registers the vehicle (has_car=True).
    """
    return ai_service.handle_slot_scan(db, data)