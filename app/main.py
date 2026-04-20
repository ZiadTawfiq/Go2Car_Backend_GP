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
from app.routes.auth import router as auth_router
from app.routes.vehicles import router as vehicles_router
from app.routes.slots import router as slots_router
from app.routes.ai import router as ai_router
from app.routes.admin import router as admin_router
from app.routes.user import router as user_router


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
app.include_router(auth_router)
app.include_router(vehicles_router)
app.include_router(slots_router)
app.include_router(ai_router)
app.include_router(admin_router)
app.include_router(user_router)
@app.get("/", tags=["Health"])
def root():
    """Health-check endpoint."""
    return {"message": f"Welcome to {settings.APP_NAME} API ", "status": "running"}
