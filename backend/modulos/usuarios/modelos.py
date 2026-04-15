"""Modelos ORM minimos del modulo usuarios."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base_class import Base
from backend.modulos.roles.modelos import Rol

if TYPE_CHECKING:
    from backend.modulos.sesiones.modelos import Sesion


class Usuario(Base):
    """Tabla de usuarios utilizada por el flujo inicial de login."""

    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    rut: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    id_rol: Mapped[int] = mapped_column(ForeignKey("roles.id_rol"), nullable=False)
    tema_preferido: Mapped[str | None] = mapped_column(String(20), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    rol: Mapped[Rol] = relationship(back_populates="usuarios")
    sesiones: Mapped[list["Sesion"]] = relationship(back_populates="usuario")
