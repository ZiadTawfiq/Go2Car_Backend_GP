"""
Shared FastAPI dependencies:
  - get_db              → database session
  - get_current_user    → any authenticated user
  - get_current_admin   → admin-only routes
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract user from JWT token.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # decode token
    try:
        payload = decode_access_token(token)
    except Exception:
        raise credentials_exception

    # get user_id from token
    user_id = payload.get("sub")
    if user_id is None or not str(user_id).isdigit():
        raise credentials_exception

    # get user from DB
    user = db.get(User, int(user_id))
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