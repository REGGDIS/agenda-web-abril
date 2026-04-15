"""Rutas de comprobacion controlada para sesiones."""

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult


router = APIRouter(prefix="/sesiones", tags=["sesiones"])


@router.get("/status")
def sesiones_status() -> dict[str, str]:
    return {"module": "sesiones", "status": "session-base-ready"}


@router.get("/actual", response_model=SesionActualResponse)
def current_session_status(
    result: SesionResolutionResult = Depends(get_current_session_result),
) -> JSONResponse:
    """Permite comprobar el estado de la cookie y la sesion actual."""

    return JSONResponse(
        status_code=result.http_status,
        content=jsonable_encoder(result.response),
    )
