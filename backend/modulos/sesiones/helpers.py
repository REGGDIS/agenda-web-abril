"""Helpers HTTP y de vista para sesiones protegidas."""

from __future__ import annotations

from fastapi.responses import RedirectResponse

from backend.app.config.settings import get_settings
from backend.modulos.sesiones.servicios import SesionResolutionResult


settings = get_settings()


def build_login_redirect_response(
    session_result: SesionResolutionResult,
) -> RedirectResponse:
    """Redirige al login y limpia la cookie de sesion cuando corresponde."""

    login_url = "/login"
    if session_result.response.status == "session_expired":
        login_url = "/login?session_expired=1"

    response = RedirectResponse(url=login_url, status_code=303)
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
    )
    return response


def build_session_monitor_context() -> dict[str, object]:
    """Expone configuracion minima del monitor de inactividad al frontend."""

    inactivity_timeout_ms = settings.session_inactivity_minutes * 60 * 1000
    return {
        "session_monitor_enabled": True,
        "session_inactivity_timeout_ms": inactivity_timeout_ms,
        "session_activity_throttle_ms": 15000,
        "session_activity_url": "/sesiones/actividad",
        "session_expire_url": "/sesiones/expirar-por-inactividad",
        "session_expired_login_url": "/login?session_expired=1",
    }
