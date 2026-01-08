from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime

from app.db.session import get_db
from app.db.models.transaction import Transaction, TransactionStatus
from app.db.models.user import User
from app.schemas.transaction import TransactionOut, TransactionCreate, TransactionUpdateStatus
from app.schemas.user import BaseResponse
from app.api.routes.auth import get_current_user
from app.utils.cloudinary import upload_image

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# 🟢 CREATE Transaction
@router.post("/", response_model=BaseResponse)
def create_transaction(
    userId: int = Form(...),
    reportedByUserId: Optional[int] = Form(None),
    amount: float = Form(...),
    transaction_date: datetime = Form(...),
    periode_id: Optional[int] = Form(None),
    payment_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Upload image
    image_url = upload_image(file)

    new_transaction = Transaction(
        amount=amount,
        transaction_date=transaction_date,
        bukti_transfer_url=image_url,
        periode_id=periode_id,
        payment_id=payment_id,
        reported_by_id=reportedByUserId or current_user.id,
        user_id=userId,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return BaseResponse(
        code=200,
        message="Transaction submitted successfully",
        data=TransactionOut.from_orm(new_transaction),
    )


# 🟠 UPDATE STATUS (Admin only)
@router.put("/{transaction_id}/status", response_model=BaseResponse)
def update_transaction_status(
    transaction_id: int,
    request: TransactionUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update transaction status")

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.status = request.status
    transaction.confirmed_by_id = current_user.id
    db.commit()
    db.refresh(transaction)

    return BaseResponse(
        code=200,
        message=f"Transaction status updated to {transaction.status.value}",
        data=TransactionOut.from_orm(transaction),
    )


# 🟡 GET ALL Transactions (with multiple filters)
@router.get("/", response_model=BaseResponse)
def get_all_transactions(
    periode_id: Optional[int] = Query(None),
    status: Optional[TransactionStatus] = Query(None),
    payment_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Transaction)
        .options(
            joinedload(Transaction.reported_by),
            joinedload(Transaction.confirmed_by),
            joinedload(Transaction.payment),
            joinedload(Transaction.periode),
        )
    )

    if current_user.user_type != "admin":
        query = query.filter(Transaction.reported_by_id == current_user.id)
    elif user_id is not None:
        # If admin AND user_id is provided, filter by that user
        query = query.filter(Transaction.reported_by_id == user_id)

    if periode_id is not None:
        query = query.filter(Transaction.periode_id == periode_id)
    if status is not None:
        query = query.filter(Transaction.status == status)
    if payment_id is not None:
        query = query.filter(Transaction.payment_id == payment_id)

    transactions = query.order_by(Transaction.created_at.desc()).all()

    data = [TransactionOut.from_orm(t) for t in transactions]

    return BaseResponse(
        code=200,
        message="Transactions fetched successfully",
        data=data,
    )


# 🔴 DELETE Transaction (Admin only)
@router.delete("/{transaction_id}", response_model=BaseResponse)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete transactions")

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()

    return BaseResponse(code=200, message="Transaction deleted successfully", data=None)
