# app/api/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from typing import Optional

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserResponse, BaseResponse, UserUpdate
from app.api.routes.auth import get_current_user


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
    request: UserUpdate,
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
        request.user_type = None
        request.username = None
        request.email = None

    # Apply updates
    update_data = request.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        user.password = hash_password(update_data["password"])
        del update_data["password"]

    for field, value in update_data.items():
        setattr(user, field, value)

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
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Restrict update of sensitive fields
    forbidden_fields = ["user_type", "email", "username"]
    for field in forbidden_fields:
        if getattr(request, field):
            raise HTTPException(
                status_code=400,
                detail=f"You are not allowed to update '{field}'"
            )

    user = current_user  # direct reference

    if request.fullname:
        user.fullname = request.fullname
    if request.phone_number:
        user.phone_number = request.phone_number
    if request.domisili:
        user.domisili = request.domisili
    if request.image_profile_url:
        user.image_profile_url = request.image_profile_url
    if request.password:
        user.password = hash_password(request.password)

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