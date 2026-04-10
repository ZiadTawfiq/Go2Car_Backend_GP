"""
ParkingSlot model — represents a physical parking space in the facility.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id = Column(Integer, primary_key=True, index=True)
    slot_code = Column(String, unique=True, index=True, nullable=False)  # e.g. F2-A-05
    floor = Column(Integer, nullable=False)
    is_occupied = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
