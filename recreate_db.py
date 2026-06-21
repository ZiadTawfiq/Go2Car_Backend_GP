import os
from sqlalchemy import create_engine
from app.db.database import Base, settings
# Import all models to ensure they are registered on Base.metadata
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.parking_record import ParkingRecord
from app.models.parking_slot import ParkingSlot
from app.models.parking_floor import ParkingFloor
from app.models.parking_section import ParkingSection
from app.models.camera import Camera
from app.models.reservation import Reservation
from app.models.blacklist_token import BlacklistedToken

# Identify all databases to recreate
db_urls = [settings.DATABASE_URL]
sqlite_fallback = "sqlite:///./go2car.db"

# If the active DB in .env is not SQLite, also recreate the local SQLite file
if "sqlite" not in settings.DATABASE_URL:
    db_urls.append(sqlite_fallback)

# Make unique list
db_urls = list(dict.fromkeys(db_urls))

print("⚠️ Warning: This will drop and recreate tables for the following databases:")
for url in db_urls:
    print(f" - {url}")

confirm = input("\nAre you sure you want to proceed? (y/N): ")

if confirm.lower() == 'y':
    for url in db_urls:
        print(f"\n⚙️ Processing database: {url}")
        
        # SQLite clean file reset
        if "sqlite" in url:
            db_path = url.replace("sqlite:///", "")
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                    print(f"  🗑️ Deleted existing SQLite file: {db_path}")
                except Exception as e:
                    print(f"  ⚠️ Could not delete SQLite file directly ({str(e)}), dropping tables instead.")

        try:
            # Create a dedicated engine for this URL
            connect_args = {"check_same_thread": False} if "sqlite" in url else {}
            eng = create_engine(url, connect_args=connect_args)
            
            print("  Dropping all tables...")
            Base.metadata.drop_all(bind=eng)
            
            print("  Creating all tables...")
            Base.metadata.create_all(bind=eng)
            
            eng.dispose()
            print("  🎉 Recreated successfully!")
        except Exception as e:
            print(f"  ❌ Error recreating database {url}: {e}")
            
    print("\n🎉 All database tables recreated successfully!")
else:
    print("Operation cancelled.")
