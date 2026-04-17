"""Esquema de detalle para una actividad del calendario."""

from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel


class ActividadDetalleData(BaseModel):
    """Representa la informacion completa visible en la pantalla de detalle."""

    id_actividad: int
    titulo: str
    descripcion: str | None = None
    fecha_actividad: date
    hora_inicio: time
    hora_fin: time
    emoji: str | None = None
    realizada: bool
    lugar: str | None = None
    categoria_nombre: str | None = None
    categoria_descripcion: str | None = None
    id_usuario: int
    usuario_nombre: str | None = None
    usuario_rut: str | None = None
    fecha_creacion: datetime
