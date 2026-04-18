"""
User model — stores registered users and admins.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from app.db.database import Base
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # bcrypt hashed

    is_admin = Column(Boolean, default=False)

    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())