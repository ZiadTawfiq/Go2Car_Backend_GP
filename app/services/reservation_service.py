"""
Reservation service — handles slot booking business logic, 
overlapping reservation checks, and automatic vehicle registration.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.reservation import Reservation, ReservationStatus
from app.models.parking_slot import ParkingSlot
from app.models.vehicle import Vehicle
from app.models.user import User
from app.schemas.reservation import ReservationCreate
from app.utils import normalize_plate


def create_reservation(db: Session, user_id: int, data: ReservationCreate) -> Reservation:
    """
    Creates a new reservation for a parking slot.
    Automatically registers the vehicle if it's new and links it to the user.
    Prevents duplicate or overlapping bookings for the same slot.
    """
    # 1. Validate timeframe
    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time."
        )
    
    # Check if booking is in the past
    now = datetime.now(timezone.utc)
    # Ensure timezone awareness for comparison
    start_time_utc = data.start_time.astimezone(timezone.utc)
    end_time_utc = data.end_time.astimezone(timezone.utc)
    
    if start_time_utc < now - datetime.resolution:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book a reservation in the past."
        )

    # 2. Check user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # 3. Check slot exists
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_code == data.slot_code).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parking slot '{data.slot_code}' does not exist."
        )

    # 4. Upsert vehicle and assign ownership
    plate = normalize_plate(data.plate_number)
    if not plate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plate number is required."
        )

    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if not vehicle:
        vehicle = Vehicle(
            plate_number=plate,
            color=None,
            vehicle_type=None
        )
        db.add(vehicle)
        db.flush()
    
    if user not in vehicle.owners:
        vehicle.owners.append(user)
        db.flush()

    # 5. Overlap protection: Check if slot is already reserved/occupied in the timeframe
    # Query reservations that overlap: (res.start_time < end_time) AND (res.end_time > start_time)
    overlap_exists = db.query(Reservation).filter(
        Reservation.slot_id == slot.id,
        Reservation.status.in_([ReservationStatus.pending, ReservationStatus.active]),
        Reservation.start_time < end_time_utc,
        Reservation.end_time > start_time_utc
    ).first()

    if overlap_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Slot '{data.slot_code}' is already reserved during the requested timeframe."
        )

    # 6. Create the reservation
    reservation = Reservation(
        user_id=user_id,
        slot_id=slot.id,
        vehicle_id=vehicle.id,
        start_time=start_time_utc,
        end_time=end_time_utc,
        status=ReservationStatus.pending
    )
    
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def get_user_reservations(db: Session, user_id: int) -> list[Reservation]:
    """
    Returns all reservations for a specific user.
    """
    return db.query(Reservation).filter(Reservation.user_id == user_id).order_by(Reservation.created_at.desc()).all()


def cancel_reservation(db: Session, user_id: int, reservation_id: int) -> Reservation:
    """
    Allows a user to cancel their own reservation.
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found."
        )

    if reservation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to cancel this reservation."
        )

    if reservation.status not in [ReservationStatus.pending, ReservationStatus.active]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel reservation with status '{reservation.status.value}'."
        )

    reservation.status = ReservationStatus.cancelled
    db.commit()
    db.refresh(reservation)
    return reservation


def get_all_reservations(db: Session) -> list[Reservation]:
    """
    Returns all reservations in the system for admin view.
    """
    return db.query(Reservation).order_by(Reservation.created_at.desc()).all()


def approve_reservation(db: Session, reservation_id: int) -> Reservation:
    """
    Allows an admin to approve/accept a reservation.
    Changes status to 'active', marks the slot as occupied,
    and inserts a record in the parking_records table.
    """
    from app.models.parking_record import ParkingRecord

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found."
        )

    if reservation.status != ReservationStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve reservation with status '{reservation.status.value}'. Only PENDING reservations can be approved."
        )

    # Check if slot is occupied
    slot = reservation.slot
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot associated with reservation not found."
        )

    if slot.is_occupied:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parking slot '{slot.slot_code}' is currently occupied."
        )

    # Update status to active
    reservation.status = ReservationStatus.active
    
    # Note: We do NOT mark slot as occupied or create a ParkingRecord here.
    # The slot status will dynamically show as "booked" due to the active reservation,
    # and a ParkingRecord will be created once the vehicle physically enters/parks.

    db.commit()
    db.refresh(reservation)
    return reservation


def reject_reservation(db: Session, reservation_id: int) -> Reservation:
    """
    Allows an admin to reject/decline a pending or active reservation.
    Changes status to 'cancelled'.
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found."
        )

    if reservation.status not in [ReservationStatus.pending, ReservationStatus.active]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject reservation with status '{reservation.status.value}'."
        )

    reservation.status = ReservationStatus.cancelled
    db.commit()
    db.refresh(reservation)
    return reservation


