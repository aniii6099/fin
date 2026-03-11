from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache(maxsize=1)
def get_session_factory():
    return SessionLocal
