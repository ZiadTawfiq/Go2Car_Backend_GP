import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.services.reservation_service import create_reservation, cancel_reservation
from app.models.reservation import Reservation, ReservationStatus
from app.models.parking_slot import ParkingSlot
from app.models.user import User
from app.schemas.reservation import ReservationCreate

class TestReservationService(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        
    def test_create_reservation_invalid_time(self):
        now = datetime.now(timezone.utc)
        data = ReservationCreate(
            slot_code="A1",
            plate_number="ABC-123",
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=1)
        )
        
        with self.assertRaises(HTTPException) as context:
            create_reservation(self.db, 1, data)
            
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Start time must be before end time.")

    def test_create_reservation_past_time(self):
        now = datetime.now(timezone.utc)
        data = ReservationCreate(
            slot_code="A1",
            plate_number="ABC-123",
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1)
        )
        
        with self.assertRaises(HTTPException) as context:
            create_reservation(self.db, 1, data)
            
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Cannot book a reservation in the past.")

    def test_cancel_reservation_success(self):
        # Setup
        user_id = 1
        reservation_id = 100
        reservation = Reservation(id=reservation_id, user_id=user_id, status=ReservationStatus.pending)
        
        self.db.query.return_value.filter.return_value.first.return_value = reservation
        
        # Execute
        result = cancel_reservation(self.db, user_id, reservation_id)
        
        # Assert
        self.assertEqual(result.status, ReservationStatus.cancelled)
        self.assertTrue(self.db.commit.called)
        self.assertTrue(self.db.refresh.called)

    def test_cancel_reservation_unauthorized(self):
        # Setup
        user_id = 1
        wrong_user_id = 2
        reservation_id = 100
        reservation = Reservation(id=reservation_id, user_id=wrong_user_id, status=ReservationStatus.pending)
        
        self.db.query.return_value.filter.return_value.first.return_value = reservation
        
        # Execute & Assert
        with self.assertRaises(HTTPException) as context:
            cancel_reservation(self.db, user_id, reservation_id)
            
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "You are not authorized to cancel this reservation.")

if __name__ == '__main__':
    unittest.main()
