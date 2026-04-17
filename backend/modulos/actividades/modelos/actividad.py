"""Modelo ORM minimo para la tabla actividades."""

from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base_class import Base
from backend.modulos.categorias.modelos import Categoria
from backend.modulos.usuarios.modelos import Usuario


class Actividad(Base):
    """Actividad real mostrada en el calendario de abril."""

    __tablename__ = "actividades"

    id_actividad: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_actividad: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
    emoji: Mapped[str | None] = mapped_column(String(20), nullable=True)
    realizada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    lugar: Mapped[str | None] = mapped_column(String(150), nullable=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)
    id_categoria: Mapped[int] = mapped_column(
        ForeignKey("categorias.id_categoria"),
        nullable=False,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    usuario: Mapped[Usuario] = relationship(back_populates="actividades")
    categoria: Mapped[Categoria] = relationship(back_populates="actividades")
