"""
Pydantic schemas for User — used for request validation and response serialization.
"""
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Request body for registration."""
    email: EmailStr
    password: str
    is_admin: bool = False


class UserLogin(BaseModel):
    """Request body for login."""
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Response schema — never expose the password."""
    id: int
    email: str
    is_admin: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
