from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class UserType(str, Enum):
    admin = "admin"
    member = "member"

class UserBase(BaseModel):
    fullname: str
    username: str
    email: EmailStr
    phone_number: Optional[str] = None
    is_active: bool = True
    domisili: Optional[str] = None
    user_type: UserType = UserType.member
    image_profile_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True
