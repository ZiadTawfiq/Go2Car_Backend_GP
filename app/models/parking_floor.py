"""
ParkingFloor model — represents a physical parking floor in the facility.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class ParkingFloor(Base):
    __tablename__ = "parking_floors"

    id = Column(Integer, primary_key=True, index=True)
    floor_code = Column(String, unique=True, index=True, nullable=False)  # e.g. F2-A-05
    floor_name = Column(String, nullable=False)

    # Relationship
    sections = relationship("ParkingSection", back_populates="floor")
    
