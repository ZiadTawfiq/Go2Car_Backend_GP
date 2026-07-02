"""
Parking Structure Seed Script
==============================
Seeds the complete garage structure (Floors, Sections, Cameras, Parking Slots)
by parsing the hierarchy from `garage_structure.txt`.

This script is idempotent — running it multiple times will NOT create duplicate records.

Run with:
    python seed_parking_structure.py
"""

from dotenv import load_dotenv
# Load environment variables from .env
load_dotenv()

import os
import re
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import settings
from app.models.parking_floor import ParkingFloor
from app.models.parking_section import ParkingSection
from app.models.parking_slot import ParkingSlot
from app.models.camera import Camera


# ---------------------------------------------------------------------------
# Garage Structure Parser
# ---------------------------------------------------------------------------

def parse_garage_structure(filepath: str) -> dict:
    """
    Parse the garage_structure.txt file and return a structured dictionary.

    Returns:
        {
            "F1": {
                "sections": {
                    "F1_A1": ["F1_A1_1", "F1_A1_2", "F1_A1_3", "F1_A1_4"],
                    ...
                }
            },
            ...
        }
    """
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    garage = {}
    current_floor = None
    current_section = None

    for line in lines:
        # Strip tree-drawing characters and whitespace to extract the name
        name = re.sub(r"[│├└─┐┌┘┤┬┴┼\s]", "", line.strip())
        if not name or name == "Garage":
            continue

        # Determine depth by counting leading special characters / whitespace
        # Floor names match: F1, F2, F3 (exactly two chars)
        # Section names match: F1_A1, F2_C3, etc. (pattern: F{digit}_{letter}{digit})
        # Slot names match: F1_A1_1, F2_C3_4, etc. (pattern: F{digit}_{letter}{digit}_{digit})

        if re.match(r"^F\d+$", name):
            # This is a floor
            current_floor = name
            garage[current_floor] = {"sections": {}}
            current_section = None

        elif re.match(r"^F\d+_[A-Z]\d+$", name):
            # This is a section
            current_section = name
            if current_floor and current_floor in garage:
                garage[current_floor]["sections"][current_section] = []

        elif re.match(r"^F\d+_[A-Z]\d+_\d+$", name):
            # This is a slot
            if current_floor and current_section:
                garage[current_floor]["sections"][current_section].append(name)

    return garage


# ---------------------------------------------------------------------------
# Seed Logic
# ---------------------------------------------------------------------------

def seed_parking_structure():
    """Seed the complete garage structure into the database."""

    # Resolve the path to garage_structure.txt relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    structure_file = os.path.join(base_dir, "garage_structure.txt")

    # Parse the hierarchy
    garage = parse_garage_structure(structure_file)

    if not garage:
        print("❌ No garage structure found in the file. Aborting.")
        sys.exit(1)

    print(f"📂 Parsed garage_structure.txt: "
          f"{len(garage)} floors, "
          f"{sum(len(s) for s in [f['sections'] for f in garage.values()])} sections")

    # Identify all databases to seed (mirrors the approach in seed.py)
    db_urls = [settings.DATABASE_URL]
    sqlite_fallback = "sqlite:///./go2car.db"

    if "sqlite" not in settings.DATABASE_URL:
        db_urls.append(sqlite_fallback)

    # Make unique list
    db_urls = list(dict.fromkeys(db_urls))

    print("\n🌱 Starting parking structure seed for:")
    for url in db_urls:
        print(f"  - {url}")

    for url in db_urls:
        print(f"\n{'=' * 55}")
        print(f"🔌 Seeding Parking Structure: {url}")
        print(f"{'=' * 55}")

        connect_args = {"check_same_thread": False} if "sqlite" in url else {}
        engine = create_engine(url, connect_args=connect_args)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = Session()

        # Counters
        floors_created = 0
        floors_skipped = 0
        sections_created = 0
        sections_skipped = 0
        cameras_created = 0
        cameras_skipped = 0
        slots_created = 0
        slots_skipped = 0

        try:
            # =========================================================
            # Seed Floors → Sections → Cameras → Slots
            # =========================================================
            for floor_code, floor_data in garage.items():
                # --- Floor ---
                floor_number = floor_code.replace("F", "")
                floor_name = f"Floor {floor_number}"

                floor = db.query(ParkingFloor).filter(
                    ParkingFloor.floor_code == floor_code
                ).first()

                if not floor:
                    floor = ParkingFloor(
                        floor_code=floor_code,
                        floor_name=floor_name,
                    )
                    db.add(floor)
                    db.flush()  # Get the id without committing
                    floors_created += 1
                    print(f"\n  ✅ Floor created: {floor_code} ({floor_name})")
                else:
                    floors_skipped += 1
                    print(f"\n  ℹ️  Floor already exists: {floor_code}")

                # --- Sections ---
                for section_code, slot_codes in floor_data["sections"].items():
                    section = db.query(ParkingSection).filter(
                        ParkingSection.section_code == section_code
                    ).first()

                    if not section:
                        section_name = f"Section {section_code}"
                        section = ParkingSection(
                            section_code=section_code,
                            section_name=section_name,
                            floor_id=floor.id,
                        )
                        db.add(section)
                        db.flush()
                        sections_created += 1
                        print(f"    ✅ Section created: {section_code}")
                    else:
                        sections_skipped += 1

                    # --- Camera (one per section, name = section_code) ---
                    camera = db.query(Camera).filter(
                        Camera.name == section_code,
                        Camera.section_id == section.id,
                    ).first()

                    if not camera:
                        camera = Camera(
                            name=section_code,
                            location_description=f"Camera for section {section_code}",
                            section_id=section.id,
                            is_active=True,
                        )
                        db.add(camera)
                        db.flush()
                        cameras_created += 1
                        print(f"      📷 Camera created: {section_code}")
                    else:
                        cameras_skipped += 1

                    # --- Parking Slots ---
                    for slot_code in slot_codes:
                        slot = db.query(ParkingSlot).filter(
                            ParkingSlot.slot_code == slot_code
                        ).first()

                        if not slot:
                            slot = ParkingSlot(
                                slot_code=slot_code,
                                section_id=section.id,
                                is_occupied=False,
                            )
                            db.add(slot)
                            slots_created += 1
                        else:
                            slots_skipped += 1

            # Commit all changes in a single transaction
            db.commit()
            print(f"\n{'─' * 55}")
            print(f"✅ Parking structure seeded successfully for: {url}")

        except Exception as e:
            db.rollback()
            print(f"\n❌ Error during seeding database {url}: {e}")
            import traceback
            traceback.print_exc()

        finally:
            db.close()
            engine.dispose()

        # =========================================================
        # Summary
        # =========================================================
        print(f"\n{'═' * 55}")
        print("📊 SEED SUMMARY")
        print(f"{'═' * 55}")

        print("\n  Created:")
        print(f"    - {floors_created} Floors")
        print(f"    - {sections_created} Sections")
        print(f"    - {cameras_created} Cameras")
        print(f"    - {slots_created} Parking Slots")

        total_skipped = floors_skipped + sections_skipped + cameras_skipped + slots_skipped
        if total_skipped > 0:
            print("\n  Skipped (already existing):")
            if floors_skipped:
                print(f"    - {floors_skipped} Floors")
            if sections_skipped:
                print(f"    - {sections_skipped} Sections")
            if cameras_skipped:
                print(f"    - {cameras_skipped} Cameras")
            if slots_skipped:
                print(f"    - {slots_skipped} Parking Slots")

        print(f"{'═' * 55}\n")


if __name__ == "__main__":
    seed_parking_structure()
