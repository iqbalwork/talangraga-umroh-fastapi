# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings  # or your DB_URL import

# Example: postgresql+psycopg2://user:password@localhost/dbname
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ This is what you were missing:
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
