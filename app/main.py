"""
Go2Car — AI Smart Parking System
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.core.config import settings
from app.db.database import Base, engine

# =========================================================
# IMPORT MODELS (IMPORTANT FOR TABLE CREATION)
# =========================================================
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.parking_record import ParkingRecord
from app.models.parking_slot import ParkingSlot

# =========================================================
# IMPORT ROUTERS
# =========================================================
from app.routes.auth import router as auth_router
from app.routes.vehicles import router as vehicles_router
from app.routes.slots import router as slots_router
from app.routes.ai import router as ai_router
from app.routes.admin import router as admin_router
from app.routes.user import router as user_router
from app.routes.floor import router as floor_router
from app.routes.section import router as section_router
from app.routes.camera import router as camera_router
from app.routes.reservations import router as reservations_router


# =========================================================
# LOAD ENV
# =========================================================
load_dotenv()


# =========================================================
# LOGGING SETUP
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)

logger = logging.getLogger("go2car")


# =========================================================
# CREATE DATABASE TABLES
# =========================================================
Base.metadata.create_all(bind=engine)

logger.info("Database tables initialized.")


# =========================================================
# FASTAPI APP
# =========================================================
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for the Go2Car AI Smart Parking System.\n\n"
        "Handles vehicle detection data from the AI module, "
        "lets users search for their parked car, and provides admin analytics."
    ),
    version="1.0.0",
    contact={
        "name": "Go2Car Team"
    },
)


# =========================================================
# CORS
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REGISTER ROUTERS
# =========================================================
app.include_router(auth_router)
app.include_router(vehicles_router)
app.include_router(slots_router)
app.include_router(ai_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(floor_router)
app.include_router(section_router)
app.include_router(camera_router)
app.include_router(reservations_router)


# =========================================================
# ROOT ENDPOINT
# =========================================================
@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "status": "running"
    }