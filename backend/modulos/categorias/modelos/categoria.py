"""Modelo ORM minimo para la tabla categorias."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base_class import Base

if TYPE_CHECKING:
    from backend.modulos.actividades.modelos import Actividad


class Categoria(Base):
    """Categoria asociada a actividades del calendario."""

    __tablename__ = "categorias"

    id_categoria: Mapped[int] = mapped_column(primary_key=True)
    nombre_categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    actividades: Mapped[list["Actividad"]] = relationship(back_populates="categoria")
