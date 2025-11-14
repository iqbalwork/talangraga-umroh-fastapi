from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.payment import Payment
from app.db.models.user import User
from app.schemas.payment import PaymentCreate, PaymentOut
from app.schemas.user import BaseResponse
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])


# 🟢 CREATE Payment
@router.post("/", response_model=BaseResponse)
def create_payment(
    request: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only admin can create payment
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create payments")

    existing = db.query(Payment).filter(Payment.payment_name == request.payment_name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Payment name already exists")

    new_payment = Payment(
        payment_name=request.payment_name,
        payment_type=request.payment_type,
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return BaseResponse(
        code=200,
        message="Payment method created successfully",
        data=PaymentOut.from_orm(new_payment)
    )


# 🟠 UPDATE Payment
@router.put("/{payment_id}", response_model=BaseResponse)
def update_payment(
    payment_id: int,
    request: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update payments")

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.payment_name = request.payment_name
    payment.payment_type = request.payment_type
    db.commit()
    db.refresh(payment)

    return BaseResponse(
        code=200,
        message="Payment updated successfully",
        data=PaymentOut.from_orm(payment)
    )


# 🔴 DELETE Payment
@router.delete("/{payment_id}", response_model=BaseResponse)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete payments")

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    db.delete(payment)
    db.commit()

    return BaseResponse(code=200, message="Payment deleted successfully", data=None)


# 🟡 GET All Payments
@router.get("/", response_model=BaseResponse)
def get_all_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payments = db.query(Payment).order_by(Payment.payment_name.asc()).all()
    payment_list = [PaymentOut.from_orm(p) for p in payments]

    return BaseResponse(
        code=200,
        message="Payments fetched successfully",
        data=payment_list
    )
