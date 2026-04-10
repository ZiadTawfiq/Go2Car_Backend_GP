"""
User model — stores registered users and admins.
"""
from sqlalchemy import Boolean, Column, Integer, String
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)          # bcrypt hashed
    is_admin = Column(Boolean, default=False)
