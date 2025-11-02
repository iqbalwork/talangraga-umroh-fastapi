# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# Base user schema
class UserBase(BaseModel):
    fullname: str
    username: str
    email: EmailStr
    phone_number: Optional[str] = None
    domisili: Optional[str] = None
    user_type: Optional[str] = "member"
    image_profile_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserForgotPassword(BaseModel):
    email: EmailStr

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True   # ✅ new syntax for Pydantic v2

# Wrapper for API response
class BaseResponse(BaseModel):
    code: int
    message: str
    data: Optional[object] = None
