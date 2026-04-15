"""Dependencias reutilizables para leer la sesion actual desde cookie."""

from __future__ import annotations

from fastapi import Depends, Request

from backend.app.config.settings import get_settings
from backend.modulos.sesiones.servicios import (
    SesionResolutionResult,
    SesionService,
    get_sesion_service,
)


settings = get_settings()


def get_current_session_result(
    request: Request,
    sesion_service: SesionService = Depends(get_sesion_service),
) -> SesionResolutionResult:
    """Lee la cookie configurada y resuelve la sesion asociada."""

    token_sesion = request.cookies.get(settings.session_cookie_name)
    return sesion_service.resolve_session_from_token(token_sesion)
