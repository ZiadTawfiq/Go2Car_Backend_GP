"""
Unified Seed Script
===================
Creates the default Admin and Regular User accounts,
as well as the base parking floors, sections, slots, vehicles, 
active parking records, cameras, and reservations.

Demonstrates Many-to-Many vehicle ownership (multiple owners per car, multiple cars per owner).
Seeds BOTH the active database in .env and the local SQLite database if Postgres is active.

Run with:
    python seed.py
"""

from dotenv import load_dotenv
# Load environment variables from .env
load_dotenv()

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from app.db.database import settings
from app.core.security import hash_password
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.parking_floor import ParkingFloor
from app.models.parking_section import ParkingSection
from app.models.parking_slot import ParkingSlot
from app.models.parking_record import ParkingRecord
from app.models.camera import Camera
from app.models.reservation import Reservation, ReservationStatus
from app.models.blacklist_token import BlacklistedToken

def seed_database():
    # Identify all databases to seed
    db_urls = [settings.DATABASE_URL]
    sqlite_fallback = "sqlite:///./go2car.db"

    # If the active DB in .env is not SQLite, also seed the local SQLite file
    if "sqlite" not in settings.DATABASE_URL:
        db_urls.append(sqlite_fallback)

    # Make unique list
    db_urls = list(dict.fromkeys(db_urls))

    print("🌱 Starting database seed for:")
    for url in db_urls:
        print(f" - {url}")

    for url in db_urls:
        print(f"\n==================================================")
        print(f"🔌 Seeding Database: {url}")
        print(f"==================================================")
        
        connect_args = {"check_same_thread": False} if "sqlite" in url else {}
        engine = create_engine(url, connect_args=connect_args)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = Session()
        
        try:
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
                admin.password = hash_password(admin_plain_password)
                admin.is_admin = True
                admin.is_verified = True
                db.add(admin)
                db.commit()
                db.refresh(admin)
                print(f"  ℹ️  Admin already exists: {admin_email}")

            # Regular User 1
            user_email = "user@go2car.com"
            user_plain_password = "UserPassword123!"
            regular_user = db.query(User).filter(User.email == user_email).first()
            if not regular_user:
                regular_user = User(
                    name="Regular User 1",
                    email=user_email,
                    password=hash_password(user_plain_password),
                    is_admin=False,
                    is_verified=True
                )
                db.add(regular_user)
                db.commit()
                db.refresh(regular_user)
                print(f"  ✅ Regular user 1 created successfully: {user_email}")
            else:
                regular_user.password = hash_password(user_plain_password)
                regular_user.is_admin = False
                regular_user.is_verified = True
                db.add(regular_user)
                db.commit()
                db.refresh(regular_user)
                print(f"  ℹ️  Regular user 1 already exists: {user_email}")

            # Regular User 2
            user2_email = "user2@go2car.com"
            user2_plain_password = "User2Password123!"
            regular_user2 = db.query(User).filter(User.email == user2_email).first()
            if not regular_user2:
                regular_user2 = User(
                    name="Regular User 2",
                    email=user2_email,
                    password=hash_password(user2_plain_password),
                    is_admin=False,
                    is_verified=True
                )
                db.add(regular_user2)
                db.commit()
                db.refresh(regular_user2)
                print(f"  ✅ Regular user 2 created successfully: {user2_email}")
            else:
                regular_user2.password = hash_password(user2_plain_password)
                regular_user2.is_admin = False
                regular_user2.is_verified = True
                db.add(regular_user2)
                db.commit()
                db.refresh(regular_user2)
                print(f"  ℹ️  Regular user 2 already exists: {user2_email}")

            # =========================================================
            # 2. CREATE VEHICLES (Many-to-Many Ownership)
            # =========================================================
            print("\n🚗 Seeding Vehicles...")
            
            vehicles_data = [
                {"plate_number": "EGP999", "color": "White", "vehicle_type": "Sedan", "owners": [regular_user, regular_user2]},
                {"plate_number": "EGP888", "color": "Blue", "vehicle_type": "SUV", "owners": [regular_user]},
                {"plate_number": "EGP777", "color": "Red", "vehicle_type": "Hatchback", "owners": [regular_user]},
                {"plate_number": "ABC123", "color": "Black", "vehicle_type": "SUV", "owners": [admin, regular_user]}
            ]
            vehicles_dict = {}
            for v_info in vehicles_data:
                vehicle = db.query(Vehicle).filter(Vehicle.plate_number == v_info["plate_number"]).first()
                if not vehicle:
                    vehicle = Vehicle(
                        plate_number=v_info["plate_number"],
                        color=v_info["color"],
                        vehicle_type=v_info["vehicle_type"]
                    )
                    for owner in v_info["owners"]:
                        vehicle.owners.append(owner)
                    db.add(vehicle)
                    db.commit()
                    db.refresh(vehicle)
                    print(f"  ✅ Vehicle created: {vehicle.plate_number} (Owners: {[o.email for o in vehicle.owners]})")
                else:
                    for owner in v_info["owners"]:
                        if owner not in vehicle.owners:
                            vehicle.owners.append(owner)
                    db.add(vehicle)
                    db.commit()
                    db.refresh(vehicle)
                    print(f"  ℹ️  Vehicle already exists: {vehicle.plate_number} (Owners: {[o.email for o in vehicle.owners]})")
                vehicles_dict[v_info["plate_number"]] = vehicle

            # =========================================================
            # 3. CREATE FLOORS, SECTIONS, AND SLOTS
            # =========================================================
            print("\n🏢 Seeding Floors, Sections, and Slots...")
            
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

            # Legacy slot
            legacy_section = get_or_create_section("A", "Section A", floor1.id)
            slot_legacy = get_or_create_slot("A-12", legacy_section.id)

            # =========================================================
            # 4. CREATE CAMERAS
            # =========================================================
            print("\n📷 Seeding Cameras...")
            cameras_data = [
                {"name": "Camera Floor 1 Entrance", "location_description": "Entrance Floor 1", "section_id": section_a1_a2.id},
                {"name": "Camera Floor 1 exit", "location_description": "Exit Floor 1", "section_id": section_b2_b3.id},
                {"name": "Camera Floor 2 Section C", "location_description": "Floor 2 Section C1", "section_id": section_c1_c2.id}
            ]
            for cam_info in cameras_data:
                existing_cam = db.query(Camera).filter(Camera.name == cam_info["name"]).first()
                if not existing_cam:
                    camera = Camera(
                        name=cam_info["name"],
                        location_description=cam_info["location_description"],
                        section_id=cam_info["section_id"],
                        is_active=True
                    )
                    db.add(camera)
                    db.commit()
                    print(f"  ✅ Camera created: {camera.name}")

            # =========================================================
            # 5. CREATE ACTIVE PARKING RECORDS
            # =========================================================
            print("\n🅿️  Seeding Active Parking Records...")
            active_pairings = [
                (vehicles_dict["EGP999"], slot_cam1_1),
                (vehicles_dict["EGP888"], slot_cam1_2),
                (vehicles_dict["EGP777"], slot_cam1_3),
                (vehicles_dict["ABC123"], slot_legacy)
            ]

            for vehicle, slot in active_pairings:
                existing_record = db.query(ParkingRecord).filter(
                    ParkingRecord.vehicle_id == vehicle.id,
                    ParkingRecord.is_active == True
                ).first()

                if not existing_record:
                    record = ParkingRecord(
                        vehicle_id=vehicle.id,
                        slot_id=slot.id,
                        is_active=True,
                        entry_time=datetime.datetime.now(datetime.timezone.utc)
                    )
                    db.add(record)
                    
                    slot.is_occupied = True
                    db.add(slot)
                    print(f"  ✅ Created active parking record: Vehicle {vehicle.plate_number} -> Slot {slot.slot_code}")
                else:
                    print(f"  ℹ️  Active parking record already exists for vehicle {vehicle.plate_number}")

            # =========================================================
            # 6. CREATE RESERVATIONS
            # =========================================================
            print("\n📅 Seeding Reservations...")
            now = datetime.datetime.now(datetime.timezone.utc)
            reservations_data = [
                {
                    "user": regular_user,
                    "slot": slot_cam1_4,
                    "vehicle": vehicles_dict["EGP888"],
                    "start_time": now + datetime.timedelta(hours=1),
                    "end_time": now + datetime.timedelta(hours=3),
                    "status": ReservationStatus.pending
                },
                {
                    "user": regular_user2,
                    "slot": slot_cam2_2,
                    "vehicle": vehicles_dict["EGP999"],
                    "start_time": now - datetime.timedelta(minutes=30),
                    "end_time": now + datetime.timedelta(hours=2),
                    "status": ReservationStatus.active
                }
            ]
            for res_info in reservations_data:
                existing_res = db.query(Reservation).filter(
                    Reservation.user_id == res_info["user"].id,
                    Reservation.slot_id == res_info["slot"].id,
                    Reservation.status == res_info["status"]
                ).first()
                if not existing_res:
                    res = Reservation(
                        user_id=res_info["user"].id,
                        slot_id=res_info["slot"].id,
                        vehicle_id=res_info["vehicle"].id if res_info["vehicle"] else None,
                        start_time=res_info["start_time"],
                        end_time=res_info["end_time"],
                        status=res_info["status"]
                    )
                    db.add(res)
                    print(f"  ✅ Reservation created: User {res_info['user'].email} -> Slot {res_info['slot'].slot_code} ({res_info['status']})")

            # =========================================================
            # 7. CREATE BLACKLISTED TOKENS (Dummy)
            # =========================================================
            print("\n🚫 Seeding Blacklisted Tokens...")
            dummy_jti = "dummy-jti-token-uuid-12345"
            existing_token = db.query(BlacklistedToken).filter(BlacklistedToken.jti == dummy_jti).first()
            if not existing_token:
                token = BlacklistedToken(jti=dummy_jti)
                db.add(token)
                print(f"  ✅ Seeded blacklisted token: {dummy_jti}")

            db.commit()
            print(f"\n🎉 Seeding completed successfully for: {url}")

        except Exception as e:
            db.rollback()
            print(f"❌ Error during seeding database {url}: {e}")
        finally:
            db.close()
            engine.dispose()

    # Print credentials
    print("\n🔑 ===========================================")
    print("🔑 SEEDED USER CREDENTIALS (ACCROSS DATABASES)")
    print("🔑 ===========================================")
    print("🔑 Admin Credentials:")
    print(f"🔑   Email:    admin@go2car.com")
    print(f"🔑   Password: AdminPassword123!")
    print("🔑 -------------------------------------------")
    print("🔑 Regular User 1 Credentials:")
    print(f"🔑   Email:    user@go2car.com")
    print(f"🔑   Password: UserPassword123!")
    print("🔑 -------------------------------------------")
    print("🔑 Regular User 2 Credentials:")
    print(f"🔑   Email:    user2@go2car.com")
    print(f"🔑   Password: User2Password123!")
    print("🔑 ===========================================\n")

    print("🎉 All database seeds completed successfully.")

if __name__ == "__main__":
    seed_database()