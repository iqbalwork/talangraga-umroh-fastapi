from pydantic import BaseModel

class PaymentBase(BaseModel):
    payment_name: str
    payment_type: str

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int

    class Config:
        from_attributes = True
