from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.transaction import Transaction, TransactionStatus
from app.db.models.user import User
from app.schemas.transaction import (
    TransactionOut,
    TransactionCreate,
    TransactionUpdateStatus,
)
from app.schemas.user import BaseResponse
from app.api.routes.auth import get_current_user
from sqlalchemy.orm import joinedload
from typing import Optional

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# 🟢 CREATE Transaction
@router.post("/", response_model=BaseResponse)
def create_transaction(
    request: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_transaction = Transaction(
        amount=request.amount,
        transaction_date=request.transaction_date,
        bukti_transfer_url=request.bukti_transfer_url,
        periode_id=request.periode_id,
        payment_id=request.payment_id,
        reported_by_id=current_user.id,
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


# 🟡 GET All Transactions (for current user)
@router.get("/", response_model=BaseResponse)
def get_all_transactions(
    periode_id: Optional[int] = Query(None, description="Filter transactions by periode_id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Transaction)
        .options(joinedload(Transaction.reported_by), joinedload(Transaction.confirmed_by))
    )

    # Normal user: only their own transactionsfrom fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.db.session import get_db
from app.db.models.transaction import Transaction, TransactionStatus
from app.db.models.user import User
from app.schemas.transaction import TransactionOut, TransactionCreate, TransactionUpdateStatus
from app.schemas.user import BaseResponse
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# 🟢 CREATE Transaction
@router.post("/", response_model=BaseResponse)
def create_transaction(
    request: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_transaction = Transaction(
        amount=request.amount,
        transaction_date=request.transaction_date,
        bukti_transfer_url=request.bukti_transfer_url,
        periode_id=request.periode_id,
        payment_id=request.payment_id,
        reported_by_id=current_user.id,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Transaction)
        .options(
            joinedload(Transaction.reported_by),
            joinedload(Transaction.confirmed_by),
            joinedload(Transaction.payment),   # ✅ include this
            joinedload(Transaction.periode),   # ✅ and this
        )
    )

    if current_user.user_type != "admin":
        query = query.filter(Transaction.reported_by_id == current_user.id)

    if periode_id is not None:
        query = query.filter(Transaction.periode_id == periode_id)
    if status is not None:
        query = query.filter(Transaction.status == status)
    if payment_id is not None:
        query = query.filter(Transaction.payment_id == payment_id)

    transactions = query.order_by(Transaction.created_at.desc()).all()

    # ✅ Use from_orm for nested serialization
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

    if current_user.user_type != "admin":
        query = query.filter(Transaction.reported_by_id == current_user.id)

    # Optional filter by periode
    if periode_id is not None:
        query = query.filter(Transaction.periode_id == periode_id)

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
