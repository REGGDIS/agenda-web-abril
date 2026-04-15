"""Modelos ORM minimos del modulo roles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base_class import Base

if TYPE_CHECKING:
    from backend.modulos.usuarios.modelos import Usuario


class Rol(Base):
    """Tabla de roles del sistema."""

    __tablename__ = "roles"

    id_rol: Mapped[int] = mapped_column(primary_key=True)
    nombre_rol: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")
