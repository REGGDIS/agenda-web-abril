"""Configuracion base de engine y sesion SQLAlchemy."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.config.settings import get_settings


settings = get_settings()


def create_db_engine() -> Engine:
    return create_engine(
        settings.sqlalchemy_database_uri,
        future=True,
        pool_pre_ping=True,
        echo=settings.sqlalchemy_echo,
    )


engine = create_db_engine()

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
