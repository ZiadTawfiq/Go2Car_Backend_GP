"""
Seed script — creates ParkingFloors, ParkingSections, and ParkingSlots
that match the CAMERA_SLOTS configuration in the AI edge node's config.py.

Run with:
    python seed_slots.py
"""
from app.db.database import SessionLocal
from app.models.parking_floor import ParkingFloor
from app.models.parking_section import ParkingSection
from app.models.parking_slot import ParkingSlot

db = SessionLocal()


# =========================================================
# HELPER
# =========================================================
def get_or_create_floor(floor_code: str, floor_name: str) -> ParkingFloor:
    obj = db.query(ParkingFloor).filter(ParkingFloor.floor_code == floor_code).first()
    if not obj:
        obj = ParkingFloor(floor_code=floor_code, floor_name=floor_name)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        print(f"  ✅ Floor created: {floor_code}")
    else:
        print(f"  ℹ️  Floor already exists: {floor_code}")
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
    else:
        print(f"    ℹ️  Section already exists: {section_code}")
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
    else:
        print(f"      ℹ️  Slot already exists: {slot_code}")
    return obj


# =========================================================
# FLOOR 1 — Cameras 1 & 2
# =========================================================
print("\n📦 Floor 1")
floor1 = get_or_create_floor("F1", "Floor 1")

# Camera 1 — Sections A1-A2 and A2-A3
print("\n  📷 Camera 1 slots")

section_a1_a2 = get_or_create_section("A1-A2", "Section A1-A2", floor1.id)
get_or_create_slot("Cam1_Slot_1", section_a1_a2.id)
get_or_create_slot("Cam1_Slot_2", section_a1_a2.id)

section_a2_a3 = get_or_create_section("A2-A3", "Section A2-A3", floor1.id)
get_or_create_slot("Cam1_Slot_3", section_a2_a3.id)
get_or_create_slot("Cam1_Slot_4", section_a2_a3.id)

# Camera 2 — Sections B1-B2 and B2-B3
print("\n  📷 Camera 2 slots")

section_b1_b2 = get_or_create_section("B1-B2", "Section B1-B2", floor1.id)
get_or_create_slot("Cam2_Slot_1", section_b1_b2.id)
get_or_create_slot("Cam2_Slot_2", section_b1_b2.id)

section_b2_b3 = get_or_create_section("B2-B3", "Section B2-B3", floor1.id)
get_or_create_slot("Cam2_Slot_3", section_b2_b3.id)


# =========================================================
# FLOOR 2 — Camera 3
# =========================================================
print("\n📦 Floor 2")
floor2 = get_or_create_floor("F2", "Floor 2")

print("\n  📷 Camera 3 slots")
section_c1_c2 = get_or_create_section("C1-C2", "Section C1-C2", floor2.id)
get_or_create_slot("Cam3_Slot_1", section_c1_c2.id)


# =========================================================
# FLOOR 3 — Camera 4
# =========================================================
print("\n📦 Floor 3")
floor3 = get_or_create_floor("F3", "Floor 3")

print("\n  📷 Camera 4 slots")
section_d1_d2 = get_or_create_section("D1-D2", "Section D1-D2", floor3.id)
get_or_create_slot("Cam4_Slot_1", section_d1_d2.id)
get_or_create_slot("Cam4_Slot_2", section_d1_d2.id)

section_d2_d3 = get_or_create_section("D2-D3", "Section D2-D3", floor3.id)
get_or_create_slot("Cam4_Slot_3", section_d2_d3.id)
get_or_create_slot("Cam4_Slot_4", section_d2_d3.id)


# =========================================================
# DONE
# =========================================================
db.close()
print("\n✅ Slot seed completed successfully.")
