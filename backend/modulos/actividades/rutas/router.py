"""Rutas del modulo actividades."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.app.config.settings import get_settings
from backend.modulos.actividades.esquemas import ActividadCreateFormData
from backend.modulos.actividades.servicios import (
    ActividadCreateCommand,
    ActividadCreateFormQuery,
    ActividadCreateService,
    ActividadDetailQuery,
    ActividadDetailService,
    ActivityCreationPermissionDeniedError,
    ActivityCreationValidationError,
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
    get_actividad_create_service,
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


@router.get("/nueva", response_class=HTMLResponse)
def actividad_create_view(
    request: Request,
    session_result: SesionResolutionResult = Depends(get_current_session_result),
    actividad_create_service: ActividadCreateService = Depends(
        get_actividad_create_service
    ),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return RedirectResponse(url="/login", status_code=303)

    try:
        create_view = actividad_create_service.prepare_form(
            ActividadCreateFormQuery(
                actor_user_id=session_result.response.usuario.id_usuario,
                actor_role_id=session_result.response.usuario.id_rol,
            )
        )
    except ActivityCreationPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    return _render_create_template(
        request=request,
        session_result=session_result,
        create_view=create_view,
    )


@router.post("/nueva", response_class=HTMLResponse)
def actividad_create_submit(
    request: Request,
    titulo: str = Form(...),
    descripcion: str = Form(""),
    fecha_actividad: str = Form(...),
    hora_inicio: str = Form(...),
    hora_fin: str = Form(...),
    emoji: str = Form(""),
    lugar: str = Form(""),
    id_categoria: str = Form(...),
    id_usuario: str = Form(""),
    realizada: str | None = Form(default=None),
    session_result: SesionResolutionResult = Depends(get_current_session_result),
    actividad_create_service: ActividadCreateService = Depends(
        get_actividad_create_service
    ),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return RedirectResponse(url="/login", status_code=303)

    command = ActividadCreateCommand(
        actor_user_id=session_result.response.usuario.id_usuario,
        actor_role_id=session_result.response.usuario.id_rol,
        titulo=titulo,
        descripcion=descripcion,
        fecha_actividad=fecha_actividad,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        emoji=emoji,
        lugar=lugar,
        id_categoria=id_categoria,
        id_usuario=id_usuario,
        realizada=_parse_checkbox_flag(realizada),
    )

    try:
        created_activity = actividad_create_service.create(command)
    except ActivityCreationValidationError as exc:
        create_view = actividad_create_service.prepare_form(
            ActividadCreateFormQuery(
                actor_user_id=session_result.response.usuario.id_usuario,
                actor_role_id=session_result.response.usuario.id_rol,
            ),
            form_data=ActividadCreateFormData(
                titulo=titulo,
                descripcion=descripcion,
                fecha_actividad=fecha_actividad,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                emoji=emoji,
                lugar=lugar,
                id_categoria=id_categoria,
                id_usuario=id_usuario,
                realizada=_parse_checkbox_flag(realizada),
            ),
            field_errors=exc.field_errors,
            general_error=exc.general_error,
        )
        return _render_create_template(
            request=request,
            session_result=session_result,
            create_view=create_view,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except ActivityCreationPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    return RedirectResponse(
        url=f"/calendario?actividad_creada={created_activity.id_actividad}",
        status_code=303,
    )


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


def _render_create_template(
    *,
    request: Request,
    session_result: SesionResolutionResult,
    create_view,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="modulos/actividades/templates/create.html",
        context={
            "request": request,
            "app_name": settings.app_name,
            "page_title": "Nueva actividad",
            "create_view": create_view,
            "usuario_actual": session_result.response.usuario,
        },
        status_code=status_code,
    )


def _parse_checkbox_flag(raw_value: str | None) -> bool:
    if raw_value is None:
        return False
    return raw_value.strip().lower() in {"1", "true", "on", "si", "sí"}
