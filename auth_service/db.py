from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from auth_service.config import DB_URL, SCHEDULER_KEY

engine = create_engine(DB_URL, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if not SCHEDULER_KEY:
    raise RuntimeError("SCHEDULER_KEY is not set in the environment")