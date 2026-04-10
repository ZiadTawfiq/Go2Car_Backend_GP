"""
AI integration route — called by the computer vision module on vehicle detection.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.ai import AIDetectRequest, AIDetectResponse
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["AI Integration"])


@router.post("/detect", response_model=AIDetectResponse)
def detect_vehicle(data: AIDetectRequest, db: Session = Depends(get_db)):
    """
    📡 Called by the YOLO/OCR AI module when a vehicle is detected.

    Flow:
    1. Create or update vehicle record.
    2. Guard against duplicate active sessions.
    3. Create parking record.
    4. Mark slot as occupied.
    """
    return ai_service.process_detection(db, data)
