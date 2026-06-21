"""
Vehicle model — represents a registered vehicle in the system.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.database import Base

# Association table for User <-> Vehicle many-to-many relationship
user_vehicles = Table(
    "user_vehicles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("vehicle_id", Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), primary_key=True, index=True)
)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, index=True, nullable=False)
    color = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)             # sedan, SUV, truck, etc.
    
    owners = relationship("User", secondary=user_vehicles, backref="vehicles")

    @property
    def owner_ids(self):
        return [o.id for o in self.owners]


