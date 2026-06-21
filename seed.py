from app.db.database import SessionLocal

from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.parking_floor import ParkingFloor
from app.models.parking_section import ParkingSection
from app.models.parking_slot import ParkingSlot
from app.models.parking_record import ParkingRecord

db = SessionLocal()


# =========================================================
# CREATE ADMIN
# =========================================================
existing_admin = db.query(User).filter(
    User.email == "admin@go2car.com"
).first()

if not existing_admin:

    admin = User(
        name="System Admin",
        email="admin@go2car.com",
        password="admin123",
        is_admin=True,
        is_verified=True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    print("Admin created successfully")

else:
    admin = existing_admin
    print("Admin already exists")


# =========================================================
# CREATE VEHICLE
# =========================================================
existing_vehicle = db.query(Vehicle).filter(
    Vehicle.plate_number == "ABC123"
).first()

if not existing_vehicle:

    vehicle = Vehicle(
        plate_number="ABC123",
        color="Black",
        vehicle_type="SUV"
    )
    vehicle.owners.append(admin)

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    print("Vehicle created successfully")

else:
    vehicle = existing_vehicle
    print("Vehicle already exists")


# =========================================================
# CREATE FLOOR
# =========================================================
existing_floor = db.query(ParkingFloor).filter(
    ParkingFloor.floor_code == "F1"
).first()

if not existing_floor:

    floor = ParkingFloor(
        floor_code="F1",
        floor_name="First Floor"
    )

    db.add(floor)
    db.commit()
    db.refresh(floor)

    print("Floor created successfully")

else:
    floor = existing_floor
    print("Floor already exists")


# =========================================================
# CREATE SECTION
# =========================================================
existing_section = db.query(ParkingSection).filter(
    ParkingSection.section_code == "A"
).first()

if not existing_section:

    section = ParkingSection(
        section_code="A",
        section_name="Section A",
        floor_id=floor.id
    )

    db.add(section)
    db.commit()
    db.refresh(section)

    print("Section created successfully")

else:
    section = existing_section
    print("Section already exists")


# =========================================================
# CREATE PARKING SLOT
# =========================================================
existing_slot = db.query(ParkingSlot).filter(
    ParkingSlot.slot_code == "A-12"
).first()

if not existing_slot:

    slot = ParkingSlot(
        slot_code="A-12",
        section_id=section.id,
        is_occupied=True
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    print("Parking slot created successfully")

else:
    slot = existing_slot
    print("Parking slot already exists")


# =========================================================
# CREATE PARKING RECORD
# =========================================================
existing_record = db.query(ParkingRecord).filter(
    ParkingRecord.vehicle_id == vehicle.id,
    ParkingRecord.is_active == True
).first()

if not existing_record:

    record = ParkingRecord(
        vehicle_id=vehicle.id,
        slot_id=slot.id,
        is_active=True
    )

    db.add(record)
    db.commit()

    print("Parking record created successfully")

else:
    print("Parking record already exists")


# =========================================================
# DONE
# =========================================================
db.close()

print("Seed completed successfully")