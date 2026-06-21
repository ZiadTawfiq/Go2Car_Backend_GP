import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

db_url = os.getenv("DATABASE_URL")
print(f"Attempting to connect to: {db_url}")

try:
    engine = create_engine(db_url)
    # Attempt to connect to the DB
    with engine.connect() as connection:
        print("\n==================================================")
        print("🎉 SUCCESS: Connected to PostgreSQL database successfully!")
        print("==================================================")
except Exception as e:
    print("\n==================================================")
    print("❌ CONNECTION FAILED!")
    print("==================================================")
    print(str(e))
