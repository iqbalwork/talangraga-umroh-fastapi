# app/api/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from starlette.datastructures import UploadFile as StarletteUploadFile
from sqlalchemy.orm import Session
from typing import List, Union
from typing import Optional

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserResponse, BaseResponse, UserUpdate, UserChangePassword
from app.api.routes.auth import get_current_user
from app.core.security import hash_password, verify_password
from app.utils.cloudinary import upload_image


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

# ✏️ UPDATE USER (Admin OR Self)
@router.put("/{user_id}", response_model=BaseResponse)
def update_user(
    user_id: int,
    fullname: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    user_type: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    domisili: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    image_profile: Union[UploadFile, str, None] = File(None),
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

    # Apply updates checking for empty values
    if fullname and fullname.strip():
        user.fullname = fullname
    if username and username.strip():
        # Check if username exists (if changed)
        if user.username != username:
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                 raise HTTPException(status_code=400, detail="Username already registered")
        user.username = username
    if email and email.strip():
         # Check if email exists (if changed)
        if user.email != email:
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                 raise HTTPException(status_code=400, detail="Email already registered")
        user.email = email
    if user_type and user_type.strip():
        user.user_type = user_type
    if phone_number and phone_number.strip():
        user.phone_number = phone_number
    if domisili and domisili.strip():
        user.domisili = domisili
    if password and password.strip():
        user.password = hash_password(password)

    if isinstance(image_profile, (UploadFile, StarletteUploadFile)) and image_profile.filename:
        image_url = upload_image(image_profile)
        user.image_profile_url = image_url

    db.commit()
    db.refresh(user)

    return BaseResponse(
        code=200,
        message="User updated successfully",
        data=UserResponse.from_orm(user)
    )


# 🟢 UPDATE OWN PROFILE
@router.put("/me/update", response_model=BaseResponse)
def update_own_profile(
    fullname: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    domisili: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    image_profile: Union[UploadFile, str, None] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = current_user

    if fullname and fullname.strip():
        user.fullname = fullname
    if username and username.strip():
        if user.username != username:
             existing_user = db.query(User).filter(User.username == username).first()
             if existing_user:
                 raise HTTPException(status_code=400, detail="Username already registered")
        user.username = username
    if email and email.strip():
        if user.email != email:
             existing_user = db.query(User).filter(User.email == email).first()
             if existing_user:
                 raise HTTPException(status_code=400, detail="Email already registered")
        user.email = email
    if phone_number and phone_number.strip():
        user.phone_number = phone_number
    if domisili and domisili.strip():
        user.domisili = domisili
    if password and password.strip():
        user.password = hash_password(password)
    
    if isinstance(image_profile, (UploadFile, StarletteUploadFile)) and image_profile.filename:
        image_url = upload_image(image_profile)
        user.image_profile_url = image_url

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


# 🔒 CHANGE PASSWORD
@router.post("/me/change-password", response_model=BaseResponse)
def change_password(
    password_data: UserChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Password saat ini salah")
    
    # Update password
    current_user.password = hash_password(password_data.new_password)
    db.commit()
    
    return BaseResponse(
        code=200,
        message="Password berhasil diubah",
        data=None
    )