from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from app.db.database import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)