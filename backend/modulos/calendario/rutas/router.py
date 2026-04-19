"""Rutas controladas para la vista principal del calendario."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.app.config.settings import get_settings
from backend.modulos.actividades.servicios import (
    ActividadCalendarQuery,
    ActividadCalendarService,
    ActividadChecklistCommand,
    ActividadChecklistService,
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
    get_actividad_calendar_service,
    get_actividad_checklist_service,
)
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.helpers import (
    build_login_redirect_response,
    build_session_monitor_context,
)
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
    actividad_creada: int | None = None,
    actividad_eliminada: int | None = None,
    session_result: SesionResolutionResult = Depends(get_current_session_result),
    actividad_calendar_service: ActividadCalendarService = Depends(
        get_actividad_calendar_service
    ),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return build_login_redirect_response(session_result)

    calendar_data = actividad_calendar_service.get_calendar_data(
        ActividadCalendarQuery(
            user_id=session_result.response.usuario.id_usuario,
            role_id=session_result.response.usuario.id_rol,
        )
    )

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
            "calendar_data": calendar_data,
            "actividad_creada": actividad_creada,
            "actividad_eliminada": actividad_eliminada,
            **build_session_monitor_context(),
        },
    )


@router.post("/actividades/{actividad_id}/realizada")
def update_actividad_checklist(
    actividad_id: int,
    realizada: str = Form(...),
    session_result: SesionResolutionResult = Depends(get_current_session_result),
    actividad_checklist_service: ActividadChecklistService = Depends(
        get_actividad_checklist_service
    ),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return build_login_redirect_response(session_result)

    try:
        actividad_checklist_service.set_realizada(
            ActividadChecklistCommand(
                actividad_id=actividad_id,
                actor_user_id=session_result.response.usuario.id_usuario,
                actor_role_id=session_result.response.usuario.id_rol,
                realizada=_parse_realizada_flag(realizada),
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

    return RedirectResponse(url="/calendario", status_code=303)


def _parse_realizada_flag(raw_value: str) -> bool:
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "on", "si", "sí"}:
        return True
    if normalized in {"0", "false", "off", "no"}:
        return False
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Valor invalido para el estado realizada.",
    )
