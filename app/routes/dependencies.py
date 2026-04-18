"""
Shared FastAPI dependencies:
  - get_db              → database session
  - get_current_user    → any authenticated user
  - get_current_admin   → admin-only routes
"""

from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer , HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.models.blacklist_token import BlacklistedToken


# ================= DB Dependency =================
def get_db():
    """
    Create a new database session for each request.
    Ensures proper closing after request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= Auth Dependency =================
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    # print(">>> TOKEN RECEIVED:", token) # will be removed 


    payload = decode_access_token(token)
    # print(">>> PAYLOAD:", payload) # will be removed 
    if payload is None:
        raise credentials_exception

    # extract user_id
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise credentials_exception

    # extract jti
    jti = payload.get("jti")
    if jti is None:
        raise credentials_exception

    # check blacklist
    blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.jti == jti).first()
    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please login again.",
        )

    # fetch user
    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user


# ================= Admin Dependency =================
def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow only admin users.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user