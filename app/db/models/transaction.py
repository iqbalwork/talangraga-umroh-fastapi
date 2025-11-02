from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    Date,
    Text,
    TIMESTAMP,
    ForeignKey,
    Enum,
    func,
)
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class TransactionStatus(str, enum.Enum):
    sent = "sent"
    on_process = "on_process"
    completed = "completed"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    reported_date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.sent, nullable=False)
    bukti_transfer_url = Column(Text, nullable=True)
    confirmed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    periode_id = Column(Integer, ForeignKey("periodes.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # --- Relationships ---
    reported_by = relationship("User", foreign_keys=[reported_by_id], backref="transactions_reported")
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id], backref="transactions_confirmed")
    periode = relationship("Periode", backref="transactions")
    payment = relationship("Payment", backref="transactions")
