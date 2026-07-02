"""
User Seed Script
=================
Seeds the initial admin and regular user accounts into the database.

This script is idempotent — running it multiple times will NOT create duplicate users.
Existing users are left untouched.

Run with:
    python seed_users.py
"""

from dotenv import load_dotenv
# Load environment variables from .env
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import settings
from app.core.security import hash_password
from app.models.user import User


# ---------------------------------------------------------------------------
# User Definitions
# ---------------------------------------------------------------------------

USERS_TO_SEED = [
    # Admins
    {
        "name": "Admin One",
        "email": "admin1@go2car.com",
        "password": "Admin123!",
        "is_admin": True,
        "is_verified": True,
    },
    {
        "name": "Admin Two",
        "email": "admin2@go2car.com",
        "password": "Admin123!",
        "is_admin": True,
        "is_verified": True,
    },
    # Regular Users
    {
        "name": "User One",
        "email": "user1@go2car.com",
        "password": "User123!",
        "is_admin": False,
        "is_verified": True,
    },
    {
        "name": "User Two",
        "email": "user2@go2car.com",
        "password": "User123!",
        "is_admin": False,
        "is_verified": True,
    },
]


# ---------------------------------------------------------------------------
# Seed Logic
# ---------------------------------------------------------------------------

def seed_users():
    """Seed the initial user accounts into the database."""

    # Identify all databases to seed (mirrors the approach in seed.py)
    db_urls = [settings.DATABASE_URL]
    sqlite_fallback = "sqlite:///./go2car.db"

    if "sqlite" not in settings.DATABASE_URL:
        db_urls.append(sqlite_fallback)

    # Make unique list
    db_urls = list(dict.fromkeys(db_urls))

    print("🌱 Starting user seed for:")
    for url in db_urls:
        print(f"  - {url}")

    for url in db_urls:
        print(f"\n{'=' * 55}")
        print(f"🔌 Seeding Users: {url}")
        print(f"{'=' * 55}")

        connect_args = {"check_same_thread": False} if "sqlite" in url else {}
        engine = create_engine(url, connect_args=connect_args)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = Session()

        # Counters
        admins_created = 0
        admins_skipped = 0
        users_created = 0
        users_skipped = 0

        try:
            for user_info in USERS_TO_SEED:
                existing = db.query(User).filter(
                    User.email == user_info["email"]
                ).first()

                if existing:
                    role_label = "Admin" if user_info["is_admin"] else "User"
                    print(f"  ℹ️  {role_label} already exists: {user_info['email']}")
                    if user_info["is_admin"]:
                        admins_skipped += 1
                    else:
                        users_skipped += 1
                    continue

                user = User(
                    name=user_info["name"],
                    email=user_info["email"],
                    password=hash_password(user_info["password"]),
                    is_admin=user_info["is_admin"],
                    is_verified=user_info["is_verified"],
                )
                db.add(user)
                db.flush()

                role_label = "Admin" if user_info["is_admin"] else "User"
                print(f"  ✅ {role_label} created: {user_info['email']}")

                if user_info["is_admin"]:
                    admins_created += 1
                else:
                    users_created += 1

            # Commit all changes in a single transaction
            db.commit()
            print(f"\n{'─' * 55}")
            print(f"✅ User seeding completed successfully for: {url}")

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
        print(f"    - {admins_created} Admins")
        print(f"    - {users_created} Users")

        total_skipped = admins_skipped + users_skipped
        if total_skipped > 0:
            print("\n  Skipped (already existing):")
            if admins_skipped:
                print(f"    - {admins_skipped} Admins")
            if users_skipped:
                print(f"    - {users_skipped} Users")

        print(f"{'═' * 55}")

    # Print credentials for reference
    print(f"\n{'🔑' * 20}")
    print("🔑 SEEDED USER CREDENTIALS")
    print(f"{'🔑' * 20}")
    for user_info in USERS_TO_SEED:
        role_label = "Admin" if user_info["is_admin"] else "User"
        print(f"  [{role_label}] {user_info['name']}")
        print(f"    Email:    {user_info['email']}")
        print(f"    Password: {user_info['password']}")
        print()


if __name__ == "__main__":
    seed_users()
