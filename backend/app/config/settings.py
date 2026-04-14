"""Carga y expone la configuracion minima del proyecto."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"

load_dotenv(ENV_FILE)


class Settings(BaseModel):
    app_name: str = Field(default=os.getenv("APP_NAME", "Agenda Abril"))
    app_env: str = Field(default=os.getenv("APP_ENV", "development"))
    debug: bool = Field(default=os.getenv("DEBUG", "true"))
    database_url: str = Field(
        default=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://USER:PASSWORD@localhost:5432/agenda_web_abril",
        )
    )
    secret_key: str = Field(default=os.getenv("SECRET_KEY", "change-me"))
    session_cookie_name: str = Field(
        default=os.getenv("SESSION_COOKIE_NAME", "agenda_abril_session")
    )
    session_inactivity_minutes: int = Field(
        default=os.getenv("SESSION_INACTIVITY_MINUTES", "1")
    )
    april_month: int = Field(default=os.getenv("APRIL_MONTH", "4"))

    @property
    def frontend_dir(self) -> Path:
        return ROOT_DIR / "frontend"

    @property
    def templates_dir(self) -> Path:
        return self.frontend_dir / "src"

    @property
    def static_dir(self) -> Path:
        return self.frontend_dir / "public"


@lru_cache
def get_settings() -> Settings:
    return Settings()

