from sqlalchemy import (
    Column, Integer, Numeric, Enum, ForeignKey, Text,
    TIMESTAMP, DateTime, func
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
from enum import Enum as PyEnum


class TransactionStatus(str, PyEnum):
    sent = "sent"
    on_process = "on_process"
    completed = "completed"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.sent, nullable=False)
    bukti_transfer_url = Column(Text, nullable=True)

    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    periode_id = Column(Integer, ForeignKey("periodes.id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)

    reported_date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # ✅ Relationships
    reported_by = relationship("User", foreign_keys=[reported_by_id])
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id])
    payment = relationship("Payment", lazy="joined")   # ✅ this one must exist
    periode = relationship("Periode", lazy="joined")   # ✅ and this one too
