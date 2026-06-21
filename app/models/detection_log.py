from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey , Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class DetectionLog(Base):
    __tablename__ = "detection_logs"

    id = Column(Integer, primary_key=True, index=True)

    camera_id = Column(Integer, ForeignKey("cameras.id"), index=True, nullable=False)
    camera = relationship("Camera")

    slot_id = Column(Integer, ForeignKey("parking_slots.id"), index=True, nullable=True)
    slot = relationship("ParkingSlot")

    plate_number = Column(String, nullable=True)         
    vehicle_color = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)

    detected_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
    flagged_for_review = Column(Boolean, default=False)  # admin manual review flag