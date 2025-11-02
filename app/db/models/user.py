# app/db/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, Enum, TIMESTAMP, text
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class UserType(str, enum.Enum):
    admin = "admin"
    member = "member"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # add this if missing
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    domisili = Column(String(100))
    user_type = Column(Enum(UserType), default=UserType.member)
    image_profile_url = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
