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
    create_refresh_token,   # ✅ new
    SECRET_KEY,
    REFRESH_SECRET_KEY,     # ✅ new (add this to your security.py)
    ALGORITHM,
)
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Auth"])

# ----------------------------------------------------------
# HTTP Bearer authentication
# ----------------------------------------------------------
security = HTTPBearer()

# ----------------------------------------------------------
# In-memory blacklist for refresh tokens (temporary)
# ----------------------------------------------------------
BLACKLISTED_REFRESH_TOKENS: set[str] = set()

# ----------------------------------------------------------
# Helper: Get current user from Access Token
# ----------------------------------------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        exp: int = payload.get("exp")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        if exp is not None and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=401,
                detail="Access token expired, please refresh your token",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Access token expired, please refresh your token",
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or malformed token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ----------------------------------------------------------
# GET USER PROFILE
# ----------------------------------------------------------
@router.get("/profile", response_model=BaseResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return BaseResponse(
        code=200,
        message="User profile fetched successfully",
        data=UserResponse.from_orm(current_user),
    )


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
# LOGIN (email/username/phone) + issue tokens
# ----------------------------------------------------------
@router.post("/login", response_model=BaseResponse)
def login_user(request: UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            (User.email == request.identifier)
            | (User.username == request.identifier)
            | (User.phone_number == request.identifier)
        )
        .first()
    )

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="email, username, nomor HP, atau password salah")

    # Create access and refresh tokens
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return BaseResponse(
        code=200,
        message="Login successful",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user),
        },
    )

# ----------------------------------------------------------
# LOGOUT - Invalidate Refresh Token
# ----------------------------------------------------------
@router.post("/logout", response_model=BaseResponse)
def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    refresh_token = credentials.credentials

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # ✅ Add token to blacklist
    BLACKLISTED_REFRESH_TOKENS.add(refresh_token)

    return BaseResponse(
        code=200,
        message="User logged out successfully. Refresh token invalidated.",
        data=None,
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
# REFRESH ACCESS TOKEN using Refresh Token
# ----------------------------------------------------------
@router.post("/refresh", response_model=BaseResponse)
def refresh_access_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    refresh_token = credentials.credentials

    # ✅ Check blacklist
    if refresh_token in BLACKLISTED_REFRESH_TOKENS:
        raise HTTPException(status_code=401, detail="Refresh token has been invalidated")

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token({"sub": email})

    return BaseResponse(
        code=200,
        message="Access token refreshed successfully",
        data={"access_token": new_access_token, "token_type": "bearer"},
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
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=403, detail="Only admin users can delete other users"
        )

    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    if user_to_delete.id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Admin cannot delete their own account"
        )

    db.delete(user_to_delete)
    db.commit()

    return BaseResponse(code=200, message="User deleted successfully", data=None)