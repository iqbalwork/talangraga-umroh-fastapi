from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum

class TransactionStatus(str, Enum):
    sent = "sent"
    on_process = "on_process"
    completed = "completed"

class TransactionBase(BaseModel):
    amount: float
    transaction_date: date
    periode_id: int
    payment_id: int
    bukti_transfer_url: Optional[str] = None
    status: Optional[TransactionStatus] = TransactionStatus.sent

class TransactionCreate(TransactionBase):
    reported_by_id: int

class TransactionOut(TransactionBase):
    id: int
    reported_by_id: int
    confirmed_by_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
