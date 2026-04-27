"""Rutas del modulo actividades."""

from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.app.config.settings import get_settings
from backend.modulos.actividades.esquemas import ActividadCreateFormData
from backend.modulos.actividades.servicios import (
    ActividadCreateCommand,
    ActividadCreateFormQuery,
    ActividadCreateService,
    ActividadDeleteCommand,
    ActividadDeletePreview,
    ActividadDeleteQuery,
    ActividadDeleteService,
    ActividadDetailQuery,
    ActividadDetailService,
    ActividadEditCommand,
    ActividadEditQuery,
    ActividadEditService,
    ActivityCreationPermissionDeniedError,
    ActivityCreationValidationError,
    ActivityEditionValidationError,
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
    get_actividad_create_service,
    get_actividad_delete_service,
    get_actividad_detail_service,
    get_actividad_edit_service,
)
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.helpers import (
    build_login_redirect_response,
    build_session_monitor_context,
)
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
    fecha: str | None = None,
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
        if _wants_json_response(request):
            return _build_invalid_session_json_response(session_result)
        return build_login_redirect_response(session_result)

    try:
        create_view = actividad_create_service.prepare_form(
            ActividadCreateFormQuery(
                actor_user_id=session_result.response.usuario.id_usuario,
                actor_role_id=session_result.response.usuario.id_rol,
            ),
            form_data=_build_prefilled_create_form_data(fecha),
        )
    except ActivityCreationPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    return _render_activity_form_template(
        request=request,
        session_result=session_result,
        form_view=create_view,
        page_title="Nueva actividad",
        form_title="Nueva actividad de abril",
        form_eyebrow="Registro de actividad",
        form_intro=(
            "Completa los datos minimos del formulario. El sistema solo acepta "
            "actividades entre el 1 y el 30 de abril y respeta los permisos del "
            "usuario autenticado."
        ),
        form_action="/actividades/nueva",
        submit_label="Guardar actividad",
        cancel_url="/calendario",
        back_url="/calendario",
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
        if _wants_json_response(request):
            return _build_invalid_session_json_response(session_result)
        return build_login_redirect_response(session_result)

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
        if _wants_json_response(request):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    {
                        "success": False,
                        "message": exc.general_error,
                        "field_errors": exc.field_errors,
                    }
                ),
            )

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
        return _render_activity_form_template(
            request=request,
            session_result=session_result,
            form_view=create_view,
            page_title="Nueva actividad",
            form_title="Nueva actividad de abril",
            form_eyebrow="Registro de actividad",
            form_intro=(
                "Completa los datos minimos del formulario. El sistema solo acepta "
                "actividades entre el 1 y el 30 de abril y respeta los permisos del "
                "usuario autenticado."
            ),
            form_action="/actividades/nueva",
            submit_label="Guardar actividad",
            cancel_url="/calendario",
            back_url="/calendario",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except ActivityCreationPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    if _wants_json_response(request):
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(
                {
                    "success": True,
                    "message": "Actividad creada correctamente.",
                    "id_actividad": created_activity.id_actividad,
                    "titulo": created_activity.titulo,
                }
            ),
        )

    return RedirectResponse(
        url=f"/calendario?actividad_creada={created_activity.id_actividad}",
        status_code=303,
    )


@router.get("/{actividad_id}/editar", response_class=HTMLResponse)
def actividad_edit_view(
    actividad_id: int,
    request: Request,
    session_result: SesionResolutionResult = Depends(get_current_session_result),
    actividad_edit_service: ActividadEditService = Depends(get_actividad_edit_service),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return build_login_redirect_response(session_result)

    try:
        edit_view = actividad_edit_service.prepare_form(
            ActividadEditQuery(
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

    return _render_activity_form_template(
        request=request,
        session_result=session_result,
        form_view=edit_view,
        page_title="Editar actividad",
        form_title="Editar actividad de abril",
        form_eyebrow="Edicion de actividad",
        form_intro=(
            "Modifica los datos necesarios y guarda los cambios. "
            "La actividad debe seguir perteneciendo al mes de abril y "
            "los permisos se validan nuevamente en backend."
        ),
        form_action=f"/actividades/{actividad_id}/editar",
        submit_label="Guardar cambios",
        cancel_url=f"/actividades/{actividad_id}",
        back_url=f"/actividades/{actividad_id}",
    )


@router.post("/{actividad_id}/editar", response_class=HTMLResponse)
def actividad_edit_submit(
    actividad_id: int,
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
    actividad_edit_service: ActividadEditService = Depends(get_actividad_edit_service),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return build_login_redirect_response(session_result)

    command = ActividadEditCommand(
        actividad_id=actividad_id,
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
        updated_activity = actividad_edit_service.update(command)
    except ActivityEditionValidationError as exc:
        edit_view = actividad_edit_service.prepare_form(
            ActividadEditQuery(
                actividad_id=actividad_id,
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
        return _render_activity_form_template(
            request=request,
            session_result=session_result,
            form_view=edit_view,
            page_title="Editar actividad",
            form_title="Editar actividad de abril",
            form_eyebrow="Edicion de actividad",
            form_intro=(
                "Modifica los datos necesarios y guarda los cambios. "
                "La actividad debe seguir perteneciendo al mes de abril y "
                "los permisos se validan nuevamente en backend."
            ),
            form_action=f"/actividades/{actividad_id}/editar",
            submit_label="Guardar cambios",
            cancel_url=f"/actividades/{actividad_id}",
            back_url=f"/actividades/{actividad_id}",
            status_code=status.HTTP_400_BAD_REQUEST,
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

    return RedirectResponse(
        url=f"/actividades/{updated_activity.id_actividad}?actualizada=1",
        status_code=303,
    )


@router.get("/{actividad_id}/eliminar", response_class=HTMLResponse)
def actividad_delete_confirm_view(
    actividad_id: int,
    request: Request,
    session_result: SesionResolutionResult = Depends(get_current_session_result),
    actividad_delete_service: ActividadDeleteService = Depends(
        get_actividad_delete_service
    ),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return build_login_redirect_response(session_result)

    try:
        actividad_preview = actividad_delete_service.get_preview(
            ActividadDeleteQuery(
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

    return _render_delete_confirm_template(
        request=request,
        session_result=session_result,
        actividad_preview=actividad_preview,
    )


@router.post("/{actividad_id}/eliminar")
def actividad_delete_submit(
    actividad_id: int,
    session_result: SesionResolutionResult = Depends(get_current_session_result),
    actividad_delete_service: ActividadDeleteService = Depends(
        get_actividad_delete_service
    ),
):
    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        return build_login_redirect_response(session_result)

    try:
        actividad_delete_service.delete(
            ActividadDeleteCommand(
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

    return RedirectResponse(url="/calendario?actividad_eliminada=1", status_code=303)


@router.get("/{actividad_id}", response_class=HTMLResponse)
def actividad_detail_view(
    actividad_id: int,
    request: Request,
    actualizada: int | None = None,
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
        return build_login_redirect_response(session_result)

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
            "actividad_actualizada": actualizada,
            **build_session_monitor_context(),
        },
    )


def _render_activity_form_template(
    *,
    request: Request,
    session_result: SesionResolutionResult,
    form_view,
    page_title: str,
    form_title: str,
    form_eyebrow: str,
    form_intro: str,
    form_action: str,
    submit_label: str,
    cancel_url: str,
    back_url: str,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="modulos/actividades/templates/create.html",
        context={
            "request": request,
            "app_name": settings.app_name,
            "page_title": page_title,
            "create_view": form_view,
            "usuario_actual": session_result.response.usuario,
            "form_title": form_title,
            "form_eyebrow": form_eyebrow,
            "form_intro": form_intro,
            "form_action": form_action,
            "submit_label": submit_label,
            "cancel_url": cancel_url,
            "back_url": back_url,
            **build_session_monitor_context(),
        },
        status_code=status_code,
    )


def _render_delete_confirm_template(
    *,
    request: Request,
    session_result: SesionResolutionResult,
    actividad_preview: ActividadDeletePreview,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="modulos/actividades/templates/delete_confirm.html",
        context={
            "request": request,
            "app_name": settings.app_name,
            "page_title": "Eliminar actividad",
            "usuario_actual": session_result.response.usuario,
            "actividad_preview": actividad_preview,
            **build_session_monitor_context(),
        },
    )


def _parse_checkbox_flag(raw_value: str | None) -> bool:
    if raw_value is None:
        return False
    return raw_value.strip().lower() in {"1", "true", "on", "si", "sí"}


def _wants_json_response(request: Request) -> bool:
    return "application/json" in request.headers.get("accept", "").lower()


def _build_invalid_session_json_response(
    session_result: SesionResolutionResult,
) -> JSONResponse:
    response = JSONResponse(
        status_code=session_result.http_status,
        content=jsonable_encoder(
            {
                "success": False,
                "status": session_result.response.status,
                "message": session_result.response.message,
            }
        ),
    )
    response.delete_cookie(key=settings.session_cookie_name, path="/")
    return response


def _build_prefilled_create_form_data(
    raw_fecha: str | None,
) -> ActividadCreateFormData | None:
    if raw_fecha is None:
        return None

    try:
        parsed_date = date.fromisoformat(raw_fecha.strip())
    except ValueError:
        return None

    if parsed_date.month != settings.april_month:
        return None

    return ActividadCreateFormData(fecha_actividad=parsed_date.isoformat())
