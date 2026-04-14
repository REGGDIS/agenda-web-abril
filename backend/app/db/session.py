"""Configuracion minima de engine y sesion SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.config.settings import get_settings


settings = get_settings()

engine = create_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

