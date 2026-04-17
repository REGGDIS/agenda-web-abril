"""Rutas controladas para la vista principal del calendario."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.app.config.settings import get_settings
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.servicios import SesionResolutionResult


router = APIRouter(prefix="/calendario", tags=["calendario"])
settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/status")
def calendario_status() -> dict[str, str]:
    return {"module": "calendario", "status": "placeholder"}


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def calendario_view(
    request: Request,
    session_result: SesionResolutionResult = Depends(get_current_session_result),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="modulos/calendario/templates/index.html",
        context={
            "request": request,
            "app_name": settings.app_name,
            "page_title": "Calendario de Abril",
            "usuario": session_result.response.usuario,
            "sesion": session_result.response.sesion,
            "session_status": session_result.response.status,
            "ultimo_movimiento_actualizado": (
                session_result.response.ultimo_movimiento_actualizado
            ),
            "ultimo_movimiento_anterior": (
                session_result.response.ultimo_movimiento_anterior
            ),
        },
    )
