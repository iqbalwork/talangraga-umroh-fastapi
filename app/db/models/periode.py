from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, func
from app.db.base import Base

class Periode(Base):
    __tablename__ = "periodes"

    id = Column(Integer, primary_key=True, index=True)
    periode_name = Column(String(50), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
