from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.parking_section import ParkingSectionOut
from app.services import section_service
from app.db.database import get_db

router = APIRouter(prefix="/sections", tags=["Sections"])

@router.get("/all", response_model=list[ParkingSectionOut])
def get_sections(db: Session = Depends(get_db)):
    return section_service.get_all_sections(db)


@router.get("/{section_id}", response_model=ParkingSectionOut)
def get_section_by_id(section_id: int, db: Session = Depends(get_db)):
    section = section_service.get_section_by_id(db, section_id)

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="section not found"
        )

    return section
    