"""
ParkingSlot model — represents a physical parking space in the facility.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Index, text
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship

class ParkingSlot(Base):
    __tablename__ = "parking_slots"
    __table_args__ = (
        Index("idx_available_slots", "section_id", postgresql_where=text("is_occupied = false")),
    )

    id = Column(Integer, primary_key=True, index=True)
    slot_code = Column(String, unique=True, index=True, nullable=False)

    # Foreign Key → Section
    section_id = Column(Integer, ForeignKey("parking_sections.id"), index=True, nullable=False)
    # Relationship
    section = relationship("ParkingSection", back_populates="slots")

    is_occupied = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    records = relationship("ParkingRecord", back_populates="slot")

    @property
    def status(self) -> str:
        if self.is_occupied:
            return "occupied"
        # Check if there is an approved active reservation (ReservationStatus.active)
        from app.models.reservation import ReservationStatus
        for res in self.reservations:
            if res.status == ReservationStatus.active:
                return "booked"
        return "available"

    @property
    def slot_number(self) -> str:
        if self.slot_code and "_" in self.slot_code:
            return self.slot_code.split("_")[-1]
        return self.slot_code