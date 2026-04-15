"""Esquemas minimos para el flujo inicial de login."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class LoginRutRequest(BaseModel):
    """Entrada minima del login por RUT."""

    rut: str = Field(
        default="",
        description="RUT completo entregado desde el login.",
        examples=["12.345.678-5"],
    )


class UsuarioLoginData(BaseModel):
    """Resumen del usuario suficiente para el siguiente paso del login."""

    id_usuario: int
    nombre: str
    rut: str
    id_rol: int
    tema_preferido: str | None = None
    activo: bool


class SesionLoginData(BaseModel):
    """Resumen de la sesion creada durante el login."""

    id_sesion: int
    id_usuario: int
    fecha_inicio: datetime
    ultimo_movimiento: datetime
    activa: bool


class LoginRutResponse(BaseModel):
    """Respuesta del flujo inicial de login."""

    success: bool
    status: Literal[
        "validation_error",
        "access_denied",
        "user_inactive",
        "session_created",
    ]
    message: str
    rut_ingresado: str
    rut_normalizado: str | None = None
    usuario_existe: bool
    usuario: UsuarioLoginData | None = None
    sesion: SesionLoginData | None = None
    siguiente_paso: Literal[
        "corregir_rut",
        "acceso_denegado",
        "reactivar_usuario",
        "validar_sesion_activa",
    ]
