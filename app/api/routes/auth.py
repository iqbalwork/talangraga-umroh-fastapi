# app/api/routes/auth.py
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserForgotPassword,
    UserResponse,
    BaseResponse,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

# ----------------------------------------------------------
# HTTP Bearer authentication (simpler, JWT-based)
# ----------------------------------------------------------
security = HTTPBearer()


# ----------------------------------------------------------
# Helper: get current user from token
# ----------------------------------------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials  # ✅ Extract token string here

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ----------------------------------------------------------
# REGISTER
# ----------------------------------------------------------
@router.post("/register", response_model=BaseResponse)
def register_user(request: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(
        fullname=request.fullname,
        username=request.username,
        email=request.email,
        password=hash_password(request.password),
        phone_number=request.phone_number,
        domisili=request.domisili,
        user_type=request.user_type,
        image_profile_url=request.image_profile_url,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return BaseResponse(
        code=200,
        message="User registered successfully",
        data=UserResponse.from_orm(new_user),
    )


# ----------------------------------------------------------
# LOGIN
# ----------------------------------------------------------
@router.post("/login", response_model=BaseResponse)
def login_user(request: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        {"sub": user.email}, expires_delta=timedelta(days=1)
    )

    return BaseResponse(
        code=200,
        message="Login successful",
        data={"token": access_token, "user": UserResponse.from_orm(user)},
    )


# ----------------------------------------------------------
# FORGOT PASSWORD
# ----------------------------------------------------------
@router.post("/forgot-password", response_model=BaseResponse)
def forgot_password(request: UserForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    reset_token = create_access_token({"sub": user.email})
    return BaseResponse(
        code=200,
        message="Password reset link sent (simulated)",
        data={"reset_token": reset_token},
    )


# ----------------------------------------------------------
# DELETE USER (Admin only)
# ----------------------------------------------------------
@router.delete("/delete/{user_id}", response_model=BaseResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ✅ Check role
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=403, detail="Only admin users can delete other users"
        )

    user_to_delete = db.query(User).filter(User.id == user_id).first()

    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent admin from deleting themselves (optional)
    if user_to_delete.id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Admin cannot delete their own account"
        )

    db.delete(user_to_delete)
    db.commit()

    return BaseResponse(code=200, message="User deleted successfully", data=None)
