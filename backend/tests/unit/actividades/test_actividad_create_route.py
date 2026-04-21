"""Pruebas de la ruta HTML de creacion de actividades."""

from __future__ import annotations

from datetime import datetime

from backend.modulos.actividades.esquemas import (
    ActividadCreateResult,
    ActividadCreateViewData,
)
from backend.modulos.actividades.servicios import (
    ActivityCreationPermissionDeniedError,
    ActivityCreationValidationError,
    get_actividad_create_service,
)
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult
from backend.tests.conftest import get_client


class FakeCreateService:
    def __init__(self) -> None:
        self.last_command = None
        self.last_prepare_kwargs = None

    def prepare_form(self, query, **kwargs):
        self.last_prepare_kwargs = {"query": query, **kwargs}
        return ActividadCreateViewData(
            categorias=[
                {"value": 1, "label": "Trabajo"},
                {"value": 2, "label": "Estudio"},
            ],
            usuarios=[{"value": 2, "label": "Usuario Abril (11.111.111-1)"}],
            allow_user_selection=False,
            form=kwargs.get("form_data") or {},
            field_errors=kwargs.get("field_errors") or {},
            general_error=kwargs.get("general_error"),
        )

    def create(self, command):
        self.last_command = command
        return ActividadCreateResult(id_actividad=25, titulo=command.titulo)


class InvalidCreateService(FakeCreateService):
    def create(self, command):
        raise ActivityCreationValidationError(
            field_errors={"fecha_actividad": "Solo abril es valido."},
            general_error="Hay datos invalidos.",
        )


class ForbiddenCreateService(FakeCreateService):
    def create(self, command):
        raise ActivityCreationPermissionDeniedError("Sin permisos para crear aqui.")


def test_actividad_create_view_renders_form():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_create_service] = (
        lambda: FakeCreateService()
    )

    try:
        response = client.get("/actividades/nueva")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Nueva actividad de abril" in response.text
    assert 'action="/actividades/nueva"' in response.text
    assert 'action="/sesiones/cerrar"' in response.text
    assert "Cerrar sesion" in response.text
    assert "Guardar actividad" in response.text
    assert "Trabajo" in response.text


def test_actividad_create_submit_redirects_to_calendar_on_success():
    client = get_client()
    fake_service = FakeCreateService()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_create_service] = lambda: fake_service

    try:
        response = client.post(
            "/actividades/nueva",
            data={
                "titulo": "Nueva actividad",
                "descripcion": "Detalle breve",
                "fecha_actividad": "2026-04-20",
                "hora_inicio": "09:00",
                "hora_fin": "10:00",
                "emoji": "📌",
                "lugar": "Sala 1",
                "id_categoria": "1",
                "id_usuario": "2",
                "realizada": "on",
            },
            follow_redirects=False,
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 303
    assert response.headers["location"] == "/calendario?actividad_creada=25"
    assert fake_service.last_command is not None
    assert fake_service.last_command.actor_user_id == 2
    assert fake_service.last_command.id_categoria == "1"
    assert fake_service.last_command.realizada is True


def test_actividad_create_submit_rerenders_form_when_validation_fails():
    client = get_client()
    fake_service = InvalidCreateService()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_create_service] = lambda: fake_service

    try:
        response = client.post(
            "/actividades/nueva",
            data={
                "titulo": "Actividad fuera de rango",
                "descripcion": "",
                "fecha_actividad": "2026-05-02",
                "hora_inicio": "09:00",
                "hora_fin": "10:00",
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
    assert "Solo abril es valido." in response.text
    assert fake_service.last_prepare_kwargs is not None
    assert fake_service.last_prepare_kwargs["field_errors"]["fecha_actividad"] == (
        "Solo abril es valido."
    )


def test_actividad_create_submit_redirects_to_login_when_session_is_invalid():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _invalid_session_result

    try:
        response = client.post(
            "/actividades/nueva",
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


def test_actividad_create_submit_returns_403_when_permission_is_denied():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_create_service] = (
        lambda: ForbiddenCreateService()
    )

    try:
        response = client.post(
            "/actividades/nueva",
            data={
                "titulo": "Actividad bloqueada",
                "descripcion": "",
                "fecha_actividad": "2026-04-20",
                "hora_inicio": "09:00",
                "hora_fin": "10:00",
                "emoji": "",
                "lugar": "",
                "id_categoria": "1",
                "id_usuario": "1",
            },
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Sin permisos para crear aqui."


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
