"""
Pydantic schemas for User — used for request validation and response serialization.
"""
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Request body for registration."""
    name: str
    email: EmailStr
    password: str
    user_type:str


class UserLogin(BaseModel):
    """Request body for login."""
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Response schema — never expose the password."""
    id: int
    name: str
    email: str
    is_admin: bool
    user_type: str
    model_config = {"from_attributes": True}

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    token: Token
    user: UserOut
    

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name : str| None = None

class AdminUpdateUser(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    is_admin: bool | None = None

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

