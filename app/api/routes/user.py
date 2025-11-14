# app/api/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserResponse, BaseResponse
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
