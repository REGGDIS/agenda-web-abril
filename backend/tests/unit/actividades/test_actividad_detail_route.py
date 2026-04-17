"""Pruebas de la vista de detalle de actividades."""

from __future__ import annotations

from datetime import datetime, date, time

from backend.modulos.actividades.esquemas import ActividadDetalleData
from backend.modulos.actividades.servicios import (
    ActivityPermissionDeniedError,
    get_actividad_detail_service,
)
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult
from backend.tests.conftest import get_client


class FakeDetailService:
    def get_detail(self, query):
        assert query.actividad_id == 1
        assert query.actor_user_id == 2
        return ActividadDetalleData(
            id_actividad=1,
            titulo="Reunion general",
            descripcion="Revision semanal del proyecto.",
            fecha_actividad=date(2026, 4, 10),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            emoji="📌",
            realizada=False,
            lugar="Sala 1",
            categoria_nombre="Trabajo",
            categoria_descripcion="Tareas laborales",
            id_usuario=2,
            usuario_nombre="Usuario Abril",
            usuario_rut="11.111.111-1",
            fecha_creacion=datetime(2026, 4, 5, 10, 0, 0),
        )


class ForbiddenDetailService:
    def get_detail(self, query):
        raise ActivityPermissionDeniedError(
            "El usuario no tiene permisos para ver esta actividad."
        )


def test_actividad_detail_renders_visible_information():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_detail_service] = (
        lambda: FakeDetailService()
    )

    try:
        response = client.get("/actividades/1")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Detalle de actividad" in response.text
    assert "Reunion general" in response.text
    assert "Revision semanal del proyecto." in response.text
    assert "Trabajo" in response.text
    assert "Usuario Abril" in response.text
    assert "11.111.111-1" in response.text
    assert "/actividades/1/editar" in response.text
    assert "/actividades/1/eliminar" in response.text


def test_actividad_detail_redirects_to_login_when_session_is_invalid():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _invalid_session_result

    try:
        response = client.get("/actividades/1", follow_redirects=False)
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_actividad_detail_returns_403_when_permission_is_denied():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_actividad_detail_service] = (
        lambda: ForbiddenDetailService()
    )

    try:
        response = client.get("/actividades/1")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "El usuario no tiene permisos para ver esta actividad."


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
