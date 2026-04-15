"""Esquemas para inspeccionar la sesion actual."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SesionActualUsuarioData(BaseModel):
    """Resumen del usuario asociado a la sesion."""

    id_usuario: int
    nombre: str
    rut: str
    id_rol: int
    tema_preferido: str | None = None
    activo: bool


class SesionActualData(BaseModel):
    """Resumen de la sesion persistida."""

    id_sesion: int
    id_usuario: int
    fecha_inicio: datetime
    ultimo_movimiento: datetime
    fecha_cierre: datetime | None = None
    activa: bool


class SesionActualResponse(BaseModel):
    """Respuesta para comprobar el estado de la sesion actual."""

    success: bool
    status: Literal[
        "cookie_missing",
        "session_not_found",
        "session_inactive",
        "session_valid",
    ]
    message: str
    cookie_present: bool
    session_found: bool
    session_active: bool
    ultimo_movimiento_actualizado: bool
    ultimo_movimiento_anterior: datetime | None = None
    sesion: SesionActualData | None = None
    usuario: SesionActualUsuarioData | None = None
