"""
ParkingSlot model — represents a physical parking space in the facility.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id = Column(Integer, primary_key=True, index=True)
    slot_code = Column(String, unique=True, index=True, nullable=False)

    # Foreign Key → Section
    section_id = Column(Integer, ForeignKey("parking_sections.id"), nullable=False)

    # Relationship
    section = relationship("ParkingSection", back_populates="slots")

    is_occupied = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
