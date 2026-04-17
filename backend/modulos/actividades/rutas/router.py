"""Rutas del modulo actividades."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.app.config.settings import get_settings
from backend.modulos.actividades.servicios import (
    ActividadDetailQuery,
    ActividadDetailService,
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
    get_actividad_detail_service,
)
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.servicios import SesionResolutionResult


router = APIRouter(prefix="/actividades", tags=["actividades"])
settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/status")
def actividades_status() -> dict[str, str]:
    return {"module": "actividades", "status": "placeholder"}


@router.get("/{actividad_id}", response_class=HTMLResponse)
def actividad_detail_view(
    actividad_id: int,
    request: Request,
    session_result: SesionResolutionResult = Depends(get_current_session_result),
    actividad_detail_service: ActividadDetailService = Depends(
        get_actividad_detail_service
    ),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return RedirectResponse(url="/login", status_code=303)

    try:
        actividad = actividad_detail_service.get_detail(
            ActividadDetailQuery(
                actividad_id=actividad_id,
                actor_user_id=session_result.response.usuario.id_usuario,
                actor_role_id=session_result.response.usuario.id_rol,
            )
        )
    except ActivityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ActivityPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    return templates.TemplateResponse(
        request=request,
        name="modulos/actividades/templates/detail.html",
        context={
            "request": request,
            "app_name": settings.app_name,
            "page_title": "Detalle de actividad",
            "actividad": actividad,
            "usuario_actual": session_result.response.usuario,
        },
    )
