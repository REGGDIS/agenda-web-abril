"""Pruebas de la ruta HTML de edicion de actividades."""

from __future__ import annotations

from datetime import datetime

from backend.modulos.actividades.esquemas import (
    ActividadCreateViewData,
    ActividadUpdateResult,
)
from backend.modulos.actividades.servicios import (
    ActivityEditionValidationError,
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
    get_actividad_edit_service,
)
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult
from backend.tests.conftest import get_client


class FakeEditService:
    def __init__(self) -> None:
        self.last_query = None
        self.last_prepare_kwargs = None
        self.last_command = None

    def prepare_form(self, query, **kwargs):
        self.last_query = query
        self.last_prepare_kwargs = kwargs
        return ActividadCreateViewData(
            categorias=[{"value": 1, "label": "Trabajo"}],
            usuarios=[{"value": 2, "label": "Usuario Abril (11.111.111-1)"}],
            allow_user_selection=False,
            form=kwargs.get("form_data")
            or {
                "titulo": "Reunion general",
                "descripcion": "Revision semanal",
                "fecha_actividad": "2026-04-10",
                "hora_inicio": "09:00",
                "hora_fin": "10:00",
                "emoji": "📌",
                "lugar": "Sala 1",
                "id_categoria": "1",
                "id_usuario": "2",
                "realizada": False,
            },
            field_errors=kwargs.get("field_errors") or {},
            general_error=kwargs.get("general_error"),
        )

    def update(self, command):
        self.last_command = command
        return ActividadUpdateResult(id_actividad=command.actividad_id, titulo=command.titulo)


class InvalidEditService(FakeEditService):
    def update(self, command):
        raise ActivityEditionValidationError(
            field_errors={"hora_fin": "La hora de fin es invalida."},
            general_error="Hay datos invalidos.",
        )


class ForbiddenEditService(FakeEditService):
    def prepare_form(self, query, **kwargs):
        raise ActivityPermissionDeniedError(
            "El usuario no tiene permisos para editar esta actividad."
        )


class MissingEditService(FakeEditService):
    def prepare_form(self, query, **kwargs):
        raise ActivityNotFoundError(f"No existe actividad con id {query.actividad_id}.")


def test_actividad_edit_view_renders_prefilled_form():
    client = get_client()
    fake_service = FakeEditService()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_edit_service] = lambda: fake_service

    try:
        response = client.get("/actividades/5/editar")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Editar actividad de abril" in response.text
    assert 'action="/actividades/5/editar"' in response.text
    assert 'value="Reunion general"' in response.text
    assert "Guardar cambios" in response.text
    assert fake_service.last_query is not None
    assert fake_service.last_query.actividad_id == 5


def test_actividad_edit_submit_redirects_to_detail_on_success():
    client = get_client()
    fake_service = FakeEditService()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_edit_service] = lambda: fake_service

    try:
        response = client.post(
            "/actividades/5/editar",
            data={
                "titulo": "Actividad editada",
                "descripcion": "Detalle actualizado",
                "fecha_actividad": "2026-04-12",
                "hora_inicio": "10:00",
                "hora_fin": "11:00",
                "emoji": "✅",
                "lugar": "Sala 3",
                "id_categoria": "1",
                "id_usuario": "2",
                "realizada": "on",
            },
            follow_redirects=False,
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 303
    assert response.headers["location"] == "/actividades/5?actualizada=1"
    assert fake_service.last_command is not None
    assert fake_service.last_command.actividad_id == 5
    assert fake_service.last_command.realizada is True


def test_actividad_edit_submit_rerenders_form_when_validation_fails():
    client = get_client()
    fake_service = InvalidEditService()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_edit_service] = lambda: fake_service

    try:
        response = client.post(
            "/actividades/5/editar",
            data={
                "titulo": "Actividad editada",
                "descripcion": "",
                "fecha_actividad": "2026-04-12",
                "hora_inicio": "12:00",
                "hora_fin": "11:00",
                "emoji": "",
                "lugar": "",
                "id_categoria": "1",
                "id_usuario": "2",
            },
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "Hay datos invalidos." in response.text
    assert "La hora de fin es invalida." in response.text
    assert fake_service.last_prepare_kwargs is not None
    assert fake_service.last_prepare_kwargs["field_errors"]["hora_fin"] == (
        "La hora de fin es invalida."
    )


def test_actividad_edit_view_returns_403_for_forbidden_activity():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_edit_service] = (
        lambda: ForbiddenEditService()
    )

    try:
        response = client.get("/actividades/5/editar")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "El usuario no tiene permisos para editar esta actividad."
    )


def test_actividad_edit_view_returns_404_for_missing_activity():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_edit_service] = (
        lambda: MissingEditService()
    )

    try:
        response = client.get("/actividades/999/editar")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "No existe actividad con id 999."


def test_actividad_edit_submit_redirects_to_login_when_session_is_invalid():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _invalid_session_result

    try:
        response = client.post(
            "/actividades/5/editar",
            data={
                "titulo": "Actividad",
                "descripcion": "",
                "fecha_actividad": "2026-04-20",
                "hora_inicio": "09:00",
                "hora_fin": "10:00",
                "emoji": "",
                "lugar": "",
                "id_categoria": "1",
                "id_usuario": "2",
            },
            follow_redirects=False,
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def _valid_session_result() -> SesionResolutionResult:
    return SesionResolutionResult(
        http_status=200,
        response=SesionActualResponse(
            success=True,
            status="session_valid",
            message="Sesion valida.",
            cookie_present=True,
            session_found=True,
            session_active=True,
            ultimo_movimiento_actualizado=True,
            ultimo_movimiento_anterior=datetime(2026, 4, 17, 10, 0, 0),
            sesion={
                "id_sesion": 7,
                "id_usuario": 2,
                "fecha_inicio": datetime(2026, 4, 17, 9, 45, 0),
                "ultimo_movimiento": datetime(2026, 4, 17, 10, 1, 0),
                "fecha_cierre": None,
                "activa": True,
            },
            usuario={
                "id_usuario": 2,
                "nombre": "Usuario Abril",
                "rut": "11.111.111-1",
                "id_rol": 2,
                "tema_preferido": "light",
                "activo": True,
            },
        ),
    )


def _invalid_session_result() -> SesionResolutionResult:
    return SesionResolutionResult(
        http_status=401,
        response=SesionActualResponse(
            success=False,
            status="cookie_missing",
            message="Sin cookie.",
            cookie_present=False,
            session_found=False,
            session_active=False,
            ultimo_movimiento_actualizado=False,
            ultimo_movimiento_anterior=None,
            sesion=None,
            usuario=None,
        ),
    )
