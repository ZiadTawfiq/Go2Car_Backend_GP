"""
Admin service — summary analytics for the parking facility.
"""
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Optional

from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import FileResponse

from app.models import User, ParkingRecord, Vehicle
from app.models.parking_slot import ParkingSlot
from app.schemas.user import AdminUpdateUser, UserRegister
from app.services.auth_service import generate_verification_token
from app.services.user_service import get_user_by_id
from app.core.security import hash_password
from app.utils import normalize_plate
from sqlalchemy import extract, func
from fastapi.responses import FileResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter



def get_summary(db: Session) -> dict:
    """
    Return a high-level summary of parking facility usage.
    """
    total = db.query(ParkingSlot).count()
    occupied = db.query(ParkingSlot).filter(ParkingSlot.is_occupied == True).count()
    available = total - occupied
    occupancy_rate = round((occupied / total * 100), 2) if total > 0 else 0.0

    return {
        "total_slots": total,
        "occupied_slots": occupied,
        "available_slots": available,
        "occupancy_rate_percent": occupancy_rate,
    }

def get_all_users(db: Session):
    return db.query(User).all()


def create_admin_account(db: Session, data: UserRegister) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    token = generate_verification_token()

    user = User(
        email=data.email,
        password=hash_password(data.password),
        name=data.name,
        is_admin=True,
        is_verified=False,
        verification_token=token,
        verification_token_expires_at=datetime.utcnow() + timedelta(minutes=30),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"http://localhost:8000/api/auth/verify-email?token={token}")

    return user


def admin_delete_user(db: Session, admin_user: User, user_id: int):
    if not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": f"User {user_id} deleted by admin"}

def admin_update_user(db: Session, user_id: int, data: AdminUpdateUser):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = data.email

    if data.name:
        user.name = data.name

    if data.is_admin is not None:
        user.is_admin = data.is_admin

    db.commit()
    db.refresh(user)

    return user

from sqlalchemy.orm import Session

from app.models.parking_slot import ParkingSlot
from app.models.parking_record import ParkingRecord


def get_analytics_summary(db: Session):

    total_slots = db.query(ParkingSlot).count()

    occupied_slots = db.query(ParkingSlot).filter(
        ParkingSlot.is_occupied == True
    ).count()

    free_slots = total_slots - occupied_slots

    occupancy_percentage = 0

    if total_slots > 0:
        occupancy_percentage = round(
            (occupied_slots / total_slots) * 100,
            2
        )

    active_vehicles = db.query(ParkingRecord).filter(
        ParkingRecord.is_active == True
    ).count()

    return {
        "success": True,
        "data": {
            "total_slots": total_slots,
            "occupied_slots": occupied_slots,
            "free_slots": free_slots,
            "occupancy_percentage": occupancy_percentage,
            "active_vehicles": active_vehicles
        }
    }

def get_peak_hours(db: Session):

    results = (
        db.query(
            extract("hour", ParkingRecord.entry_time).label("hour"),
            ParkingRecord.id
        )
        .all()
    )

    hourly_stats = {}

    for hour, _ in results:

        hour = int(hour)

        if hour not in hourly_stats:
            hourly_stats[hour] = 0

        hourly_stats[hour] += 1

    data = [
        {
            "hour": hour,
            "entries": count
        }
        for hour, count in sorted(hourly_stats.items())
    ]

    return {
        "success": True,
        "data": data
    }
def get_heatmap_data(db: Session):

    results = (
        db.query(
            ParkingSlot,
            func.count(ParkingRecord.id).label("usage_count")
        )
        .join(
            ParkingRecord,
            ParkingRecord.slot_id == ParkingSlot.id
        )
        .group_by(ParkingSlot.id)
        .order_by(
            func.count(ParkingRecord.id).desc()
        )
        .all()
    )

    data = []

    for slot, usage_count in results:

        occupancy_rate = 0

        if usage_count > 0:
            occupancy_rate = min(
                round((usage_count / 10) * 100, 2),
                100
            )

        data.append({
            "slot": slot.slot_code,
            "section": slot.section.section_name,
            "floor": slot.section.floor.floor_name,
            "usage_count": usage_count,
            "occupancy_rate": occupancy_rate
        })

    return {
        "success": True,
        "count": len(data),
        "data": data
    }

def get_analytics_history(db: Session):

    records = (
        db.query(ParkingRecord)
        .join(
            Vehicle,
            Vehicle.id == ParkingRecord.vehicle_id
        )
        .order_by(
            ParkingRecord.entry_time.desc()
        )
        .all()
    )

    data = [
        {
            "plate_number": r.vehicle.plate_number,
            "slot": r.slot.slot_code,
            "section": r.slot.section.section_name,
            "floor": r.slot.section.floor.floor_name,
            "entry_time": r.entry_time,
            "exit_time": r.exit_time,
            "is_active": r.is_active,
            "image_path": r.image_path
        }
        for r in records
    ]

    return {
        "success": True,
        "count": len(data),
        "data": data
    }
def export_analytics_pdf(db: Session):

    records = (
        db.query(ParkingRecord)
        .join(
            Vehicle,
            Vehicle.id == ParkingRecord.vehicle_id
        )
        .order_by(
            ParkingRecord.entry_time.desc()
        )
        .all()
    )

    file_name = "parking_analytics_report.pdf"

    doc = SimpleDocTemplate(
        file_name,
        pagesize=letter
    )

    elements = []

    styles = getSampleStyleSheet()

    title = Paragraph(
        "Go2Car Parking Analytics Report",
        styles["Title"]
    )

    elements.append(title)

    elements.append(Spacer(1, 20))

    data = [[
        "Plate",
        "Slot",
        "Section",
        "Floor",
        "Entry",
        "Exit",
        "Active"
    ]]

    for r in records:

        data.append([
            r.vehicle.plate_number,
            r.slot.slot_code,
            r.slot.section.section_name,
            r.slot.section.floor.floor_name,
            str(r.entry_time),
            str(r.exit_time),
            str(r.is_active)
        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),

    ]))

    elements.append(table)

    doc.build(elements)

    return FileResponse(
        path=file_name,
        filename=file_name,
        media_type="application/pdf"
    )
