"""
Vehicle model — represents a registered vehicle in the system.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, index=True, nullable=False)
    color = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)             # sedan, SUV, truck, etc.
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", backref="vehicles")
