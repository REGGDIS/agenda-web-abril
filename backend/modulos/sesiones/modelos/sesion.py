"""Modelo ORM minimo para la tabla sesiones."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base_class import Base
from backend.modulos.usuarios.modelos import Usuario


class Sesion(Base):
    """Sesion persistida del usuario."""

    __tablename__ = "sesiones"

    id_sesion: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)
    token_sesion: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ultimo_movimiento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    usuario: Mapped[Usuario] = relationship(back_populates="sesiones")
