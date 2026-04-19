"""Rutas de comprobacion controlada para sesiones."""

from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from backend.app.config.settings import get_settings
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import (
    SesionResolutionResult,
    SesionService,
    get_sesion_service,
)


router = APIRouter(prefix="/sesiones", tags=["sesiones"])
settings = get_settings()


@router.get("/status")
def sesiones_status() -> dict[str, str]:
    return {"module": "sesiones", "status": "session-base-ready"}


@router.get("/actual", response_model=SesionActualResponse)
def current_session_status(
    result: SesionResolutionResult = Depends(get_current_session_result),
) -> JSONResponse:
    """Permite comprobar el estado de la cookie y la sesion actual."""

    response = JSONResponse(
        status_code=result.http_status,
        content=jsonable_encoder(result.response),
    )
    if not result.response.success:
        response.delete_cookie(key=settings.session_cookie_name, path="/")
    return response


@router.post("/actividad", response_model=SesionActualResponse)
def register_current_session_activity(
    request: Request,
    sesion_service: SesionService = Depends(get_sesion_service),
) -> JSONResponse:
    """Registra un movimiento basico del usuario con frecuencia controlada."""

    token_sesion = request.cookies.get(settings.session_cookie_name)
    result = sesion_service.register_activity_from_token(token_sesion)
    response = JSONResponse(
        status_code=result.http_status,
        content=jsonable_encoder(result.response),
    )
    if not result.response.success:
        response.delete_cookie(key=settings.session_cookie_name, path="/")
    return response


@router.post("/expirar-por-inactividad", response_model=SesionActualResponse)
def expire_current_session_by_inactivity(
    request: Request,
    sesion_service: SesionService = Depends(get_sesion_service),
) -> JSONResponse:
    """Cierra explicitamente la sesion actual cuando el frontend detecta inactividad."""

    token_sesion = request.cookies.get(settings.session_cookie_name)
    result = sesion_service.expire_session_from_token(token_sesion)
    response = JSONResponse(
        status_code=result.http_status,
        content=jsonable_encoder(result.response),
    )
    response.delete_cookie(key=settings.session_cookie_name, path="/")
    return response
