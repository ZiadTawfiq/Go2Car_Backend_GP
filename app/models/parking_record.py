"""
ParkingRecord model — the core table that tracks every vehicle's parking session.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime , ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship

class ParkingRecord(Base):
    __tablename__ = "parking_records"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    vehicle = relationship("Vehicle", backref="parking_records")

    # Link to ParkingSlot
    slot_id = Column(Integer, ForeignKey("parking_slots.id"), nullable=False)
    slot = relationship("ParkingSlot", back_populates="records")

    entry_time = Column(DateTime(timezone=True), server_default=func.now())
    exit_time = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True)  # True as long as the vehicle still exists
