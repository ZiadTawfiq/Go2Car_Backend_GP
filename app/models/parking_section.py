"""
ParkingSection model — represents a physical parking section in the facility.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime ,ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship

class ParkingSection(Base):
    __tablename__ = "parking_sections"

    id = Column(Integer, primary_key=True, index=True)
    section_code = Column(String, unique=True, index=True, nullable=False)  # e.g. F2-A-05
    section_name = Column(String, nullable=False)

    # Foreign Key
    floor_id = Column(Integer, ForeignKey("parking_floors.id"), index=True)
    # Relationship
    floor = relationship("ParkingFloor", back_populates="sections")

    cameras = relationship("Camera", back_populates="section", cascade="all, delete")
    slots = relationship("ParkingSlot", back_populates="section", cascade="all, delete")  

    @property
    def section_display(self) -> str:
        if self.section_code and "_" in self.section_code:
            return self.section_code.split("_")[-1]
        return self.section_code

    @property
    def section_name_display(self) -> str:
        if self.section_name:
            import re
            return re.sub(r'F\d+_', '', self.section_name)
        return self.section_name

