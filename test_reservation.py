import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.db.database import Base, settings
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.parking_slot import ParkingSlot
from app.models.reservation import Reservation, ReservationStatus
from app.schemas.reservation import ReservationCreate
from app.services.reservation_service import create_reservation, get_user_reservations, cancel_reservation

def run_tests():
    print("🔌 Connecting to database...")
    connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        print("👥 Retrieving regular user...")
        user = db.query(User).filter(User.email == "user@go2car.com").first()
        if not user:
            print("❌ Test failed: Please run seed.py first to populate the users!")
            return

        slot_code = "Cam1_Slot_4"
        plate_number = "NEWCAR123"
        
        # Ensure vehicle does not exist to test auto-registration
        existing_vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
        if existing_vehicle:
            print("🚗 Vehicle already exists, deleting it to test clean auto-registration...")
            db.delete(existing_vehicle)
            db.commit()

        # Delete any existing reservations for this slot to have a clean slate
        slot = db.query(ParkingSlot).filter(ParkingSlot.slot_code == slot_code).first()
        if slot:
            db.query(Reservation).filter(Reservation.slot_id == slot.id).delete()
            db.commit()

        print("\n🧪 Test 1: Creating a reservation for a new vehicle...")
        now = datetime.datetime.now(datetime.timezone.utc)
        res_data = ReservationCreate(
            slot_code=slot_code,
            plate_number=plate_number,
            start_time=now + datetime.timedelta(hours=5),
            end_time=now + datetime.timedelta(hours=7)
        )
        
        res = create_reservation(db, user.id, res_data)
        print("✅ Reservation created successfully!")
        print(f"   Reservation ID: {res.id}")
        print(f"   Status: {res.status.value}")
        print(f"   Linked Vehicle ID: {res.vehicle_id}")

        print("\n🧪 Test 2: Verifying vehicle was auto-registered and associated with user...")
        vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
        if vehicle:
            print(f"✅ Vehicle '{plate_number}' successfully registered!")
            if user in vehicle.owners:
                print(f"✅ User '{user.email}' successfully associated as owner!")
            else:
                print("❌ Failed: User not associated with vehicle.")
        else:
            print("❌ Failed: Vehicle was not registered.")

        print("\n🧪 Test 3: Attempting to create an overlapping reservation on the same slot...")
        overlap_data = ReservationCreate(
            slot_code=slot_code,
            plate_number="OTHERCAR99",
            start_time=now + datetime.timedelta(hours=6), # Overlaps from 6 to 8 (existing is 5 to 7)
            end_time=now + datetime.timedelta(hours=8)
        )
        
        try:
            create_reservation(db, user.id, overlap_data)
            print("❌ Failed: Overlapping reservation was allowed but should have been blocked!")
        except HTTPException as e:
            print(f"✅ Blocked successfully! Status code: {e.status_code}, Detail: {e.detail}")

        print("\n🧪 Test 4: Retrieving user reservations...")
        user_reservations = get_user_reservations(db, user.id)
        print(f"✅ Successfully retrieved {len(user_reservations)} reservations for the user.")

        print("\n🧪 Test 5: Cancelling the reservation...")
        cancelled_res = cancel_reservation(db, user.id, res.id)
        print(f"✅ Reservation cancelled successfully! New Status: {cancelled_res.status.value}")

    except Exception as e:
        print(f"❌ Error during tests: {e}")
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    run_tests()
