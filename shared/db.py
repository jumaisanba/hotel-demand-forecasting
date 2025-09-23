# shared/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.pool import NullPool  # или другой, в зависимости от среды
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Получаем URL из переменных среды (или .env)
DB_URL=f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаём engine
engine = create_engine(DB_URL, poolclass=NullPool)

# Создаём фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс моделей
Base: DeclarativeMeta = declarative_base()


# Dependency — для FastAPI маршрутов
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session_sync():
    return next(get_session())