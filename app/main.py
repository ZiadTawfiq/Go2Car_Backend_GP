"""
Go2Car — AI Smart Parking System
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
from app.routes import auth, vehicles, slots, ai, admin , floor

# ── Logging setup ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger("go2car")

# ── Create all tables on startup (SQLite / dev convenience) ─────────────────
# For PostgreSQL in production, use Alembic migrations instead.
Base.metadata.create_all(bind=engine)
logger.info("Database tables initialised.")

# ── FastAPI app ─────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for the Go2Car AI Smart Parking System.\n\n"
        "Handles vehicle detection data from the AI module, "
        "lets users search for their parked car, and provides admin analytics."
    ),
    version="1.0.0",
    contact={"name": "Go2Car Team"},
)

# ── CORS (allow all origins for development) ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(slots.router)
app.include_router(ai.router)
app.include_router(admin.router)
app.include_router(floor.router)


@app.get("/", tags=["Health"])
def root():
    """Health-check endpoint."""
    return {"message": f"Welcome to {settings.APP_NAME} API 🚗", "status": "running"}
