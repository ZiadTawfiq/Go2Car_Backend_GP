"""
API routes for managing parking slot reservations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.routes.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services import reservation_service

router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"]
)


@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a reservation",
    description="Reserve a parking slot for a specific timeframe. Registers vehicle if new."
)
def create(
    data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return reservation_service.create_reservation(db, current_user.id, data)


@router.get(
    "/me",
    response_model=List[ReservationResponse],
    summary="Get my reservations",
    description="Retrieve all reservations for the currently authenticated user."
)
def get_my_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return reservation_service.get_user_reservations(db, current_user.id)


@router.post(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse,
    summary="Cancel a reservation",
    description="Cancel a pending or active reservation."
)
def cancel(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return reservation_service.cancel_reservation(db, current_user.id, reservation_id)


@router.get(
    "/all",
    response_model=List[ReservationResponse],
    summary="Get all reservations",
    description="Retrieve all reservations in the system. Admin access required."
)
def get_all(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    return reservation_service.get_all_reservations(db)


@router.post(
    "/{reservation_id}/approve",
    response_model=ReservationResponse,
    summary="Approve a reservation",
    description="Approve a pending reservation, changing its status to active, marking the slot occupied, and creating a parking record. Admin access required."
)
def approve(
    reservation_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    return reservation_service.approve_reservation(db, reservation_id)

