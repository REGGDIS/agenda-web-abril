"""Pruebas de las rutas HTML de eliminacion de actividades."""

from __future__ import annotations

from datetime import datetime

from backend.modulos.actividades.servicios import (
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
    get_actividad_delete_service,
)
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult
from backend.tests.conftest import get_client


class FakeDeleteService:
    def __init__(self) -> None:
        self.last_query = None
        self.last_command = None

    def get_preview(self, query):
        self.last_query = query
        return {
            "id_actividad": 5,
            "titulo": "Reunion general",
            "descripcion": "Revision semanal",
            "fecha_actividad_label": "10/04/2026",
            "horario_label": "09:00 - 10:00",
            "categoria_nombre": "Trabajo",
            "usuario_nombre": "Usuario Abril",
        }

    def delete(self, command):
        self.last_command = command


class MissingDeleteService(FakeDeleteService):
    def get_preview(self, query):
        raise ActivityNotFoundError(f"No existe actividad con id {query.actividad_id}.")


class ForbiddenDeleteService(FakeDeleteService):
    def get_preview(self, query):
        raise ActivityPermissionDeniedError(
            "El usuario no tiene permisos para eliminar esta actividad."
        )

    def delete(self, command):
        raise ActivityPermissionDeniedError(
            "El usuario no tiene permisos para eliminar esta actividad."
        )


def test_actividad_delete_confirm_view_renders_confirmation():
    client = get_client()
    fake_service = FakeDeleteService()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_delete_service] = lambda: fake_service

    try:
        response = client.get("/actividades/5/eliminar")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Eliminar actividad" in response.text
    assert "Confirmar eliminacion" in response.text
    assert 'action="/actividades/5/eliminar"' in response.text
    assert "Reunion general" in response.text
    assert fake_service.last_query is not None
    assert fake_service.last_query.actividad_id == 5


def test_actividad_delete_submit_redirects_to_calendar_on_success():
    client = get_client()
    fake_service = FakeDeleteService()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_delete_service] = lambda: fake_service

    try:
        response = client.post("/actividades/5/eliminar", follow_redirects=False)
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 303
    assert response.headers["location"] == "/calendario?actividad_eliminada=1"
    assert fake_service.last_command is not None
    assert fake_service.last_command.actividad_id == 5
    assert fake_service.last_command.actor_user_id == 2


def test_actividad_delete_confirm_returns_403_when_forbidden():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_delete_service] = (
        lambda: ForbiddenDeleteService()
    )

    try:
        response = client.get("/actividades/5/eliminar")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "El usuario no tiene permisos para eliminar esta actividad."
    )


def test_actividad_delete_confirm_returns_404_when_missing():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_delete_service] = (
        lambda: MissingDeleteService()
    )

    try:
        response = client.get("/actividades/999/eliminar")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "No existe actividad con id 999."


def test_actividad_delete_submit_redirects_to_login_when_session_is_invalid():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _invalid_session_result

    try:
        response = client.post("/actividades/5/eliminar", follow_redirects=False)
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
