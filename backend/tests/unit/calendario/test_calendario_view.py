"""Pruebas de la vista principal del calendario."""

from __future__ import annotations

from datetime import datetime

from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult
from backend.tests.conftest import get_client


def test_calendario_redirects_to_login_when_session_is_invalid():
    client = get_client()

    response = client.get("/calendario", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_calendario_renders_logged_user_when_session_is_valid():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = lambda: (
        SesionResolutionResult(
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
                    "id_usuario": 1,
                    "fecha_inicio": datetime(2026, 4, 17, 9, 45, 0),
                    "ultimo_movimiento": datetime(2026, 4, 17, 10, 1, 0),
                    "fecha_cierre": None,
                    "activa": True,
                },
                usuario={
                    "id_usuario": 1,
                    "nombre": "Administrador",
                    "rut": "12.345.678-5",
                    "id_rol": 1,
                    "tema_preferido": "light",
                    "activo": True,
                },
            ),
        )
    )

    try:
        response = client.get("/calendario")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Administrador" in response.text
    assert "12.345.678-5" in response.text
    assert "session_valid" in response.text
    assert "Ultimo movimiento actual" in response.text
