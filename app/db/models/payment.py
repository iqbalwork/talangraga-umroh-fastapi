from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from app.db.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_name = Column(String(100), nullable=False)
    payment_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
