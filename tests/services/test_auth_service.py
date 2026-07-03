import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.services.auth_service import register_user, login_user
from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import hash_password

class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        
    @patch('app.services.auth_service.send_verification_email')
    def test_register_user_success(self, mock_send_email):
        # Setup
        self.db.query.return_value.filter.return_value.first.return_value = None
        data = UserRegister(email="test@test.com", password="password123", name="Test User")
        
        # Execute
        user = register_user(self.db, data)
        
        # Assert
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.name, "Test User")
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_verified)
        self.assertTrue(self.db.add.called)
        self.assertTrue(self.db.commit.called)
        mock_send_email.assert_called_once()
        
    def test_register_user_existing_email(self):
        # Setup
        existing_user = User(email="test@test.com")
        self.db.query.return_value.filter.return_value.first.return_value = existing_user
        data = UserRegister(email="test@test.com", password="password123", name="Test User")
        
        # Execute & Assert
        with self.assertRaises(HTTPException) as context:
            register_user(self.db, data)
            
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Email is already registered.")

    @patch('app.services.auth_service.verify_password')
    @patch('app.services.auth_service.create_access_token')
    def test_login_user_success(self, mock_create_token, mock_verify_password):
        # Setup
        mock_verify_password.return_value = True
        mock_create_token.return_value = "fake_token"
        
        user = User(id=1, email="test@test.com", password="hashed_password", is_verified=True, is_admin=False)
        self.db.query.return_value.filter.return_value.first.return_value = user
        
        # Execute
        result = login_user(self.db, email="test@test.com", password="password123")
        
        # Assert
        self.assertEqual(result["token"]["access_token"], "fake_token")
        self.assertEqual(result["user"], user)
        mock_verify_password.assert_called_once_with("password123", "hashed_password")
        
    @patch('app.services.auth_service.verify_password')
    def test_login_user_unverified(self, mock_verify_password):
        # Setup
        mock_verify_password.return_value = True
        user = User(id=1, email="test@test.com", password="hashed_password", is_verified=False, is_admin=False)
        self.db.query.return_value.filter.return_value.first.return_value = user
        
        # Execute & Assert
        with self.assertRaises(HTTPException) as context:
            login_user(self.db, email="test@test.com", password="password123")
            
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Please verify your email first")

if __name__ == '__main__':
    unittest.main()
