import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Index, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class ReservationStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"
    expired = "expired"



class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        Index("idx_active_reservations", "user_id", postgresql_where=text("status IN ('pending', 'active')")),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    user = relationship("User", backref="reservations")

    slot_id = Column(Integer, ForeignKey("parking_slots.id"), index=True, nullable=False)
    slot = relationship("ParkingSlot", backref="reservations")

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), index=True, nullable=True)
    vehicle = relationship("Vehicle", backref="reservations")

    start_time = Column(DateTime(timezone=True), index=True, nullable=False)
    end_time = Column(DateTime(timezone=True), index=True, nullable=False)
    
    status = Column(
        Enum(ReservationStatus, name="reservation_status"),
        default=ReservationStatus.pending,
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def user_name(self) -> str:
        return self.user.name if self.user else ""

    @property
    def user_email(self) -> str:
        return self.user.email if self.user else ""

    @property
    def plate_number(self) -> str:
        return self.vehicle.plate_number if self.vehicle else ""

    @property
    def slot_code(self) -> str:
        return self.slot.slot_code if self.slot else ""

    @property
    def slot_number(self) -> str:
        return self.slot.slot_number if self.slot else ""


