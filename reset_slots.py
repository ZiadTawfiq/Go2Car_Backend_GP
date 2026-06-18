"""
Script to reset all parking slots to unoccupied and close any active parking records.
"""
from datetime import datetime, timezone
from app.db.database import SessionLocal
from app.models.parking_slot import ParkingSlot
from app.models.parking_record import ParkingRecord

def reset_database():
    db = SessionLocal()
    try:
        # 1. Reset all slots to unoccupied
        slots_reset = db.query(ParkingSlot).filter(ParkingSlot.is_occupied == True).update(
            {ParkingSlot.is_occupied: False},
            synchronize_session=False
        )
        
        # 2. Close all active parking records
        records_closed = db.query(ParkingRecord).filter(ParkingRecord.is_active == True).update(
            {
                ParkingRecord.is_active: False,
                ParkingRecord.exit_time: datetime.now(timezone.utc)
            },
            synchronize_session=False
        )
        
        db.commit()
        print(f"✅ Reset complete:")
        print(f"   - {slots_reset} slots marked as unoccupied.")
        print(f"   - {records_closed} active parking records closed.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error resetting database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
