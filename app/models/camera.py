from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location_description = Column(String, nullable=True)

    #  Link to Section
    section_id = Column(Integer, ForeignKey("parking_sections.id"), index=True, nullable=False)
    section = relationship("ParkingSection", back_populates="cameras")

    is_active = Column(Boolean, default=True)