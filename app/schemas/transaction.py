from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
from app.schemas.payment import PaymentOut
from app.schemas.periode import PeriodeOut


class TransactionStatus(str, Enum):
    sent = "sent"
    on_process = "on_process"
    completed = "completed"


# 🧑 Simple user reference (used for reported_by / confirmed_by)
class SimpleUser(BaseModel):
    id: int
    fullname: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[str] = None

    class Config:
        from_attributes = True


# 🟢 Base Transaction structure
class TransactionBase(BaseModel):
    amount: float
    transaction_date: datetime
    bukti_transfer_url: Optional[str] = None


# 🟣 Create Transaction request body
class TransactionCreate(TransactionBase):
    periode_id: Optional[int] = None
    payment_id: Optional[int] = None


# 🟠 Update status (admin)
class TransactionUpdateStatus(BaseModel):
    status: TransactionStatus


# 🔵 Response model with nested relations
class TransactionOut(TransactionBase):
    id: int
    status: TransactionStatus
    reported_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    reported_by: Optional[SimpleUser] = None
    confirmed_by: Optional[SimpleUser] = None
    payment: Optional[PaymentOut] = None
    periode: Optional[PeriodeOut] = None

    class Config:
        from_attributes = True
