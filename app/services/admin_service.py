"""
Admin service — summary analytics for the parking facility.
"""
from sqlalchemy.orm import Session

from app.models.parking_slot import ParkingSlot


def get_summary(db: Session) -> dict:
    """
    Return a high-level summary of parking facility usage.
    """
    total = db.query(ParkingSlot).count()
    occupied = db.query(ParkingSlot).filter(ParkingSlot.is_occupied == True).count()
    available = total - occupied
    occupancy_rate = round((occupied / total * 100), 2) if total > 0 else 0.0

    return {
        "total_slots": total,
        "occupied_slots": occupied,
        "available_slots": available,
        "occupancy_rate_percent": occupancy_rate,
    }
