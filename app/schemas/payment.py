from pydantic import BaseModel
from datetime import datetime

class PaymentBase(BaseModel):
    payment_name: str
    payment_type: str

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
