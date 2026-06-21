"""
Unified Seed Script
===================
Creates the default Admin and Regular User accounts (with properly hashed passwords),
as well as the base parking floors, sections, slots, vehicles, and active parking records.

Credentials for Development/Testing:

# Admin Credentials:
# Email: admin@go2car.com
# Password: AdminPassword123!

# User Credentials:
# Email: user@go2car.com
# Password: UserPassword123!

Run with:
    python seed.py
"""
import datetime
from sqlalchemy.sql import func
from app.db.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.parking_floor import ParkingFloor
from app.models.parking_section import ParkingSection
from app.models.parking_slot import ParkingSlot
from app.models.parking_record import ParkingRecord

def seed_database():
    db = SessionLocal()
    try:
        print("🌱 Starting database seed...")

        # =========================================================
        # 1. CREATE USERS (Idempotent)
        # =========================================================
        print("\n👥 Seeding Users...")
        
        # Admin User
        admin_email = "admin@go2car.com"
        admin_plain_password = "AdminPassword123!"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                name="System Admin",
                email=admin_email,
                password=hash_password(admin_plain_password),
                is_admin=True,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"  ✅ Admin created successfully: {admin_email}")
        else:
            # Safely update password to match plain password in case it was modified
            admin.password = hash_password(admin_plain_password)
            admin.is_admin = True
            admin.is_verified = True
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"  ℹ️  Admin already exists (updated successfully): {admin_email}")

        # Regular User
        user_email = "user@go2car.com"
        user_plain_password = "UserPassword123!"
        regular_user = db.query(User).filter(User.email == user_email).first()
        if not regular_user:
            regular_user = User(
                name="Regular User",
                email=user_email,
                password=hash_password(user_plain_password),
                is_admin=False,
                is_verified=True
            )
            db.add(regular_user)
            db.commit()
            db.refresh(regular_user)
            print(f"  ✅ Regular user created successfully: {user_email}")
        else:
            # Safely update password to match plain password in case it was modified
            regular_user.password = hash_password(user_plain_password)
            regular_user.is_admin = False
            regular_user.is_verified = True
            db.add(regular_user)
            db.commit()
            db.refresh(regular_user)
            print(f"  ℹ️  Regular user already exists (updated successfully): {user_email}")

        # =========================================================
        # 2. CREATE VEHICLES
        # =========================================================
        print("\n🚗 Seeding Vehicles...")
        vehicles_data = [
            {"plate_number": "EGP999", "color": "White", "vehicle_type": "Sedan", "owner_id": regular_user.id},
            {"plate_number": "EGP888", "color": "Blue", "vehicle_type": "SUV", "owner_id": regular_user.id},
            {"plate_number": "EGP777", "color": "Red", "vehicle_type": "Hatchback", "owner_id": regular_user.id},
            {"plate_number": "ABC123", "color": "Black", "vehicle_type": "SUV", "owner_id": admin.id}
        ]
        vehicles_dict = {}
        for v_info in vehicles_data:
            vehicle = db.query(Vehicle).filter(Vehicle.plate_number == v_info["plate_number"]).first()
            if not vehicle:
                vehicle = Vehicle(
                    plate_number=v_info["plate_number"],
                    color=v_info["color"],
                    vehicle_type=v_info["vehicle_type"],
                    owner_id=v_info["owner_id"]
                )
                db.add(vehicle)
                db.commit()
                db.refresh(vehicle)
                print(f"  ✅ Vehicle created: {vehicle.plate_number}")
            else:
                print(f"  ℹ️  Vehicle already exists: {vehicle.plate_number}")
            vehicles_dict[v_info["plate_number"]] = vehicle

        # =========================================================
        # 3. CREATE FLOORS, SECTIONS, AND SLOTS
        # =========================================================
        print("\n🏢 Seeding Floors, Sections, and Slots...")
        
        # Helper functions
        def get_or_create_floor(floor_code: str, floor_name: str) -> ParkingFloor:
            obj = db.query(ParkingFloor).filter(ParkingFloor.floor_code == floor_code).first()
            if not obj:
                obj = ParkingFloor(floor_code=floor_code, floor_name=floor_name)
                db.add(obj)
                db.commit()
                db.refresh(obj)
                print(f"  ✅ Floor created: {floor_code}")
            return obj

        def get_or_create_section(section_code: str, section_name: str, floor_id: int) -> ParkingSection:
            obj = db.query(ParkingSection).filter(ParkingSection.section_code == section_code).first()
            if not obj:
                obj = ParkingSection(
                    section_code=section_code,
                    section_name=section_name,
                    floor_id=floor_id,
                )
                db.add(obj)
                db.commit()
                db.refresh(obj)
                print(f"    ✅ Section created: {section_code}")
            return obj

        def get_or_create_slot(slot_code: str, section_id: int) -> ParkingSlot:
            obj = db.query(ParkingSlot).filter(ParkingSlot.slot_code == slot_code).first()
            if not obj:
                obj = ParkingSlot(
                    slot_code=slot_code,
                    section_id=section_id,
                    is_occupied=False,
                )
                db.add(obj)
                db.commit()
                db.refresh(obj)
                print(f"      ✅ Slot created: {slot_code}")
            return obj

        # Floor 1
        floor1 = get_or_create_floor("F1", "Floor 1")
        section_a1_a2 = get_or_create_section("A1-A2", "Section A1-A2", floor1.id)
        slot_cam1_1 = get_or_create_slot("Cam1_Slot_1", section_a1_a2.id)
        slot_cam1_2 = get_or_create_slot("Cam1_Slot_2", section_a1_a2.id)

        section_a2_a3 = get_or_create_section("A2-A3", "Section A2-A3", floor1.id)
        slot_cam1_3 = get_or_create_slot("Cam1_Slot_3", section_a2_a3.id)
        slot_cam1_4 = get_or_create_slot("Cam1_Slot_4", section_a2_a3.id)

        section_b1_b2 = get_or_create_section("B1-B2", "Section B1-B2", floor1.id)
        slot_cam2_1 = get_or_create_slot("Cam2_Slot_1", section_b1_b2.id)
        slot_cam2_2 = get_or_create_slot("Cam2_Slot_2", section_b1_b2.id)

        section_b2_b3 = get_or_create_section("B2-B3", "Section B2-B3", floor1.id)
        slot_cam2_3 = get_or_create_slot("Cam2_Slot_3", section_b2_b3.id)

        # Floor 2
        floor2 = get_or_create_floor("F2", "Floor 2")
        section_c1_c2 = get_or_create_section("C1-C2", "Section C1-C2", floor2.id)
        slot_cam3_1 = get_or_create_slot("Cam3_Slot_1", section_c1_c2.id)

        # Floor 3
        floor3 = get_or_create_floor("F3", "Floor 3")
        section_d1_d2 = get_or_create_section("D1-D2", "Section D1-D2", floor3.id)
        slot_cam4_1 = get_or_create_slot("Cam4_Slot_1", section_d1_d2.id)
        slot_cam4_2 = get_or_create_slot("Cam4_Slot_2", section_d1_d2.id)

        section_d2_d3 = get_or_create_section("D2-D3", "Section D2-D3", floor3.id)
        slot_cam4_3 = get_or_create_slot("Cam4_Slot_3", section_d2_d3.id)
        slot_cam4_4 = get_or_create_slot("Cam4_Slot_4", section_d2_d3.id)

        # Legacy slot from old seed.py
        legacy_section = get_or_create_section("A", "Section A", floor1.id)
        slot_legacy = get_or_create_slot("A-12", legacy_section.id)

        # =========================================================
        # 4. CREATE ACTIVE PARKING RECORDS
        # =========================================================
        print("\n🅿️  Seeding Active Parking Records...")
        
        # Let's map vehicles to specific slots for seeding active records
        active_pairings = [
            (vehicles_dict["EGP999"], slot_cam1_1),
            (vehicles_dict["EGP888"], slot_cam1_2),
            (vehicles_dict["EGP777"], slot_cam1_3),
            (vehicles_dict["ABC123"], slot_legacy)
        ]

        for vehicle, slot in active_pairings:
            # Check if this vehicle already has an active record
            existing_record = db.query(ParkingRecord).filter(
                ParkingRecord.vehicle_id == vehicle.id,
                ParkingRecord.is_active == True
            ).first()

            if not existing_record:
                # Create the active record
                record = ParkingRecord(
                    vehicle_id=vehicle.id,
                    slot_id=slot.id,
                    is_active=True,
                    entry_time=datetime.datetime.now(datetime.timezone.utc)
                )
                db.add(record)
                
                # Mark slot as occupied
                slot.is_occupied = True
                db.add(slot)
                print(f"  ✅ Created active parking record: Vehicle {vehicle.plate_number} -> Slot {slot.slot_code}")
            else:
                print(f"  ℹ️  Active parking record already exists for vehicle {vehicle.plate_number} (in Slot {slot.slot_code})")

        db.commit()

        # Print the credentials clearly to the console
        print("\n🔑 ===========================================")
        print("🔑 SEEDED USER CREDENTIALS")
        print("🔑 ===========================================")
        print("🔑 Admin Credentials:")
        print(f"🔑   Email:    {admin_email}")
        print(f"🔑   Password: {admin_plain_password}")
        print("🔑 -------------------------------------------")
        print("🔑 User Credentials:")
        print(f"🔑   Email:    {user_email}")
        print(f"🔑   Password: {user_plain_password}")
        print("🔑 ===========================================\n")

        print("🎉 Database seed completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()