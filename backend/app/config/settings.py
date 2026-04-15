"""Carga y expone la configuracion tipada del proyecto."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import BaseModel, Field


ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"

load_dotenv(ENV_FILE)


TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "f", "no", "n", "off"}


def _get_env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    cleaned_value = value.strip()
    return cleaned_value if cleaned_value else default


def _get_env_optional_str(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    cleaned_value = value.strip()
    return cleaned_value or None


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def _get_env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default

    normalized_value = value.strip().lower()
    if normalized_value in TRUE_VALUES:
        return True
    if normalized_value in FALSE_VALUES:
        return False

    return default


class Settings(BaseModel):
    app_name: str = Field(default="Agenda Abril")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    database_url: str | None = Field(default=None)
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="agenda_web_abril")
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    sqlalchemy_echo: bool = Field(default=False)
    secret_key: str = Field(default="change-me")
    session_cookie_name: str = Field(default="agenda_abril_session")
    session_inactivity_minutes: int = Field(default=1)
    april_month: int = Field(default=4)

    @property
    def frontend_dir(self) -> Path:
        return ROOT_DIR / "frontend"

    @property
    def templates_dir(self) -> Path:
        return self.frontend_dir / "src"

    @property
    def static_dir(self) -> Path:
        return self.frontend_dir / "public"

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url

        quoted_user = quote_plus(self.postgres_user)
        quoted_password = quote_plus(self.postgres_password)
        return (
            f"postgresql+psycopg://{quoted_user}:{quoted_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    settings = Settings(
        app_name=_get_env_str("APP_NAME", "Agenda Abril"),
        app_env=_get_env_str("APP_ENV", "development"),
        debug=_get_env_bool("DEBUG", True),
        database_url=_get_env_optional_str("DATABASE_URL"),
        postgres_host=_get_env_str("POSTGRES_HOST", "localhost"),
        postgres_port=_get_env_int("POSTGRES_PORT", 5432),
        postgres_db=_get_env_str("POSTGRES_DB", "agenda_web_abril"),
        postgres_user=_get_env_str("POSTGRES_USER", "postgres"),
        postgres_password=_get_env_str("POSTGRES_PASSWORD", "postgres"),
        sqlalchemy_echo=_get_env_bool("SQLALCHEMY_ECHO", False),
        secret_key=_get_env_str("SECRET_KEY", "change-me"),
        session_cookie_name=_get_env_str(
            "SESSION_COOKIE_NAME", "agenda_abril_session"
        ),
        session_inactivity_minutes=_get_env_int("SESSION_INACTIVITY_MINUTES", 1),
        april_month=_get_env_int("APRIL_MONTH", 4),
    )

    if settings.april_month != 4:
        raise ValueError("Agenda Abril solo admite APRIL_MONTH=4.")

    return settings
