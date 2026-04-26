"""Pruebas del cambio de estado de actividades desde el calendario."""

from __future__ import annotations

from datetime import datetime

from backend.modulos.actividades.servicios import (
    ActivityPermissionDeniedError,
    get_actividad_checklist_service,
)
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult
from backend.tests.conftest import get_client


class FakeChecklistService:
    def __init__(self) -> None:
        self.last_command = None

    def set_realizada(self, command):
        self.last_command = command
        return {"id_actividad": command.actividad_id, "realizada": command.realizada}


class ForbiddenChecklistService:
    def set_realizada(self, command):
        raise ActivityPermissionDeniedError("Sin permisos para esta actividad.")


def test_calendario_checklist_updates_activity_and_redirects():
    client = get_client()
    fake_service = FakeChecklistService()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_checklist_service] = lambda: fake_service

    try:
        response = client.post(
            "/calendario/actividades/8/realizada",
            data={"realizada": "true"},
            follow_redirects=False,
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 303
    assert response.headers["location"] == "/calendario"
    assert fake_service.last_command is not None
    assert fake_service.last_command.actividad_id == 8
    assert fake_service.last_command.actor_user_id == 2
    assert fake_service.last_command.actor_role_id == 2
    assert fake_service.last_command.realizada is True


def test_calendario_checklist_returns_json_when_requested_by_mobile_client():
    client = get_client()
    fake_service = FakeChecklistService()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_checklist_service] = lambda: fake_service

    try:
        response = client.post(
            "/calendario/actividades/8/realizada",
            data={"realizada": "false"},
            headers={"Accept": "application/json"},
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Estado de actividad actualizado.",
        "id_actividad": 8,
        "realizada": False,
    }
    assert fake_service.last_command is not None
    assert fake_service.last_command.realizada is False


def test_calendario_checklist_redirects_to_login_when_session_is_invalid():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _invalid_session_result

    try:
        response = client.post(
            "/calendario/actividades/8/realizada",
            data={"realizada": "true"},
            follow_redirects=False,
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_calendario_checklist_returns_json_error_when_mobile_session_is_invalid():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _invalid_session_result

    try:
        response = client.post(
            "/calendario/actividades/8/realizada",
            data={"realizada": "true"},
            headers={"Accept": "application/json"},
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["message"] == "Sin cookie."


def test_calendario_checklist_returns_403_for_forbidden_activity():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_checklist_service] = (
        lambda: ForbiddenChecklistService()
    )

    try:
        response = client.post(
            "/calendario/actividades/8/realizada",
            data={"realizada": "false"},
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Sin permisos para esta actividad."


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
