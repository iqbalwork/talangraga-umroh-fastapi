from pydantic import BaseModel
from datetime import date, datetime

class PeriodeBase(BaseModel):
    periode_name: str
    start_date: date
    end_date: date

class PeriodeCreate(PeriodeBase):
    pass

class PeriodeOut(PeriodeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
