"""
ParkingRecord model — the core table that tracks every vehicle's parking session.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class ParkingRecord(Base):
    __tablename__ = "parking_records"

    id = Column(Integer, primary_key=True, index=True)

    plate_number = Column(String, index=True, nullable=False)

    # Link to ParkingSlot
    slot_id = Column(Integer, ForeignKey("parking_slots.id"), nullable=False)

    slot = relationship("ParkingSlot")

    entry_time = Column(DateTime(timezone=True), server_default=func.now())
    exit_time = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True)
