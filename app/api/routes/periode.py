# app/api/routes/periode.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.periode import Periode
from app.schemas.periode import PeriodeCreate, PeriodeOut
from app.schemas.user import BaseResponse
from app.api.routes.auth import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/periodes", tags=["Periodes"])


# 🟢 CREATE Periode
@router.post("/", response_model=BaseResponse)
def create_periode(
    request: PeriodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Optional: allow only admin to create periode
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create periode."
        )

    # Check duplicate periode_name
    existing = db.query(Periode).filter(Periode.periode_name == request.periode_name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Periode name already exists.")

    if request.start_date >= request.end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date.")

    new_periode = Periode(
        periode_name=request.periode_name,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    db.add(new_periode)
    db.commit()
    db.refresh(new_periode)

    return BaseResponse(
        code=200,
        message="Periode created successfully",
        data=PeriodeOut.from_orm(new_periode)
    )


# 🟠 UPDATE Periode
@router.put("/{periode_id}", response_model=BaseResponse)
def update_periode(
    periode_id: int,
    request: PeriodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update periode.")

    periode = db.query(Periode).filter(Periode.id == periode_id).first()
    if not periode:
        raise HTTPException(status_code=404, detail="Periode not found")

    if request.start_date >= request.end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date.")

    periode.periode_name = request.periode_name
    periode.start_date = request.start_date
    periode.end_date = request.end_date

    db.commit()
    db.refresh(periode)

    return BaseResponse(
        code=200,
        message="Periode updated successfully",
        data=PeriodeOut.from_orm(periode)
    )


# 🔴 DELETE Periode
@router.delete("/{periode_id}", response_model=BaseResponse)
def delete_periode(
    periode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete periode.")

    periode = db.query(Periode).filter(Periode.id == periode_id).first()
    if not periode:
        raise HTTPException(status_code=404, detail="Periode not found")

    db.delete(periode)
    db.commit()

    return BaseResponse(code=200, message="Periode deleted successfully", data=None)


# 🟡 GET ALL Periodes
@router.get("/", response_model=BaseResponse)
def get_all_periodes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    periodes = db.query(Periode).order_by(Periode.start_date.asc()).all()
    periode_list = [PeriodeOut.from_orm(p) for p in periodes]

    return BaseResponse(
        code=200,
        message="Periodes fetched successfully",
        data=periode_list
    )
