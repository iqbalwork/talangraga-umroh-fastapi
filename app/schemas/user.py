# app/schemas/user.py
from pydantic import BaseModel, EmailStr, validator
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
    identifier: str
    password: str

class UserForgotPassword(BaseModel):
    email: EmailStr

class UserChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserResetPassword(BaseModel):
    reset_token: str
    new_password: str
    confirm_new_password: str

    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    domisili: Optional[str] = None
    user_type: Optional[str] = None
    password: Optional[str] = None
    image_profile_url: Optional[str] = None

    class Config:
        from_attributes = True

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
