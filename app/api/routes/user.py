# app/api/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserResponse, BaseResponse
from app.api.routes.auth import get_current_user
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


# 🟡 GET ALL USERS (Admin only)
@router.get("/", response_model=BaseResponse)
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Restrict access to admin only
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this endpoint"
        )

    users = db.query(User).order_by(User.created_at.desc()).all()
    user_list = [UserResponse.from_orm(u) for u in users]

    return BaseResponse(
        code=200,
        message="Users fetched successfully",
        data=user_list
    )


# 🟢 GET SINGLE USER BY ID (Admin only)
@router.get("/{user_id}", response_model=BaseResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this endpoint"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return BaseResponse(
        code=200,
        message="User fetched successfully",
        data=UserResponse.from_orm(user)
    )


# ✏️ UPDATE USER (Admin OR Self) (Form Data & File Upload)
@router.put("/{user_id}", response_model=BaseResponse)
def update_user(
    user_id: int,
    fullname: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    domisili: Optional[str] = Form(None),
    user_type: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch user to update
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission check: admin OR self
    if current_user.user_type != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this user"
        )

    # Restrict sensitive fields for non-admin
    if current_user.user_type != "admin":
        user_type = None
        username = None
        email = None

    # Handle image upload if provided
    if file:
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        timestamp = int(datetime.utcnow().timestamp())
        safe_filename = file.filename or f"profile_{user.username or user_id}_{timestamp}.jpg"
        file_path = os.path.join(upload_dir, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        user.image_profile_url = f"/static/uploads/{safe_filename}"

    # Apply other updates
    if fullname is not None:
        user.fullname = fullname
    if username is not None:
        # Check uniqueness if username is changing
        if username != user.username:
            if db.query(User).filter(User.username == username).first():
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = username
    if email is not None:
        # Check uniqueness if email is changing
        if email != user.email:
            if db.query(User).filter(User.email == email).first():
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = email
    if phone_number is not None:
        user.phone_number = phone_number
    if domisili is not None:
        user.domisili = domisili
    if user_type is not None:
        user.user_type = user_type
    if password is not None and password != "":
        user.password = hash_password(password)

    db.commit()
    db.refresh(user)

    return BaseResponse(
        code=200,
        message="User updated successfully",
        data=UserResponse.from_orm(user)
    )


# 🟢 UPDATE OWN PROFILE (Form Data & File Upload)
@router.put("/me/update", response_model=BaseResponse)
def update_own_profile(
    fullname: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    domisili: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = current_user  # direct reference

    # Handle image upload if provided
    if file:
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        timestamp = int(datetime.utcnow().timestamp())
        safe_filename = file.filename or f"profile_{user.username}_{timestamp}.jpg"
        file_path = os.path.join(upload_dir, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        user.image_profile_url = f"/static/uploads/{safe_filename}"

    if fullname is not None:
        user.fullname = fullname
    if phone_number is not None:
        user.phone_number = phone_number
    if domisili is not None:
        user.domisili = domisili
    if password is not None and password != "":
        user.password = hash_password(password)

    db.commit()
    db.refresh(user)

    return BaseResponse(
        code=200,
        message="Profile updated successfully",
        data=UserResponse.from_orm(user)
    )


# ❌ DELETE USER (Admin only)
@router.delete("/{user_id}", response_model=BaseResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete users")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return BaseResponse(code=200, message="User deleted successfully", data=None)