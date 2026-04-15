"""Pruebas de la ruta inicial de login."""

from __future__ import annotations

from datetime import datetime

from backend.app.config.settings import get_settings
from backend.modulos.auth.esquemas.login import LoginRutResponse
from backend.modulos.auth.servicios.login_service import (
    LoginExecutionResult,
    get_auth_service,
)
from backend.tests.conftest import get_client


class FakeAuthService:
    def prepare_login(self, rut: str) -> LoginExecutionResult:
        return LoginExecutionResult(
            http_status=200,
            response=LoginRutResponse(
                success=True,
                status="session_created",
                message=f"RUT recibido: {rut}",
                rut_ingresado=rut,
                rut_normalizado="12345678-5",
                usuario_existe=True,
                usuario=None,
                sesion={
                    "id_sesion": 77,
                    "id_usuario": 1,
                    "fecha_inicio": datetime(2026, 4, 15, 10, 0, 0),
                    "ultimo_movimiento": datetime(2026, 4, 15, 10, 0, 0),
                    "activa": True,
                },
                siguiente_paso="validar_sesion_activa",
            ),
            session_cookie_token="token-router-test",
        )


def test_auth_login_accepts_json_payload():
    client = get_client()
    client.app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    try:
        response = client.post("/auth/login", json={"rut": "12.345.678-5"})
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["message"] == "RUT recibido: 12.345.678-5"
    assert response.cookies.get(get_settings().session_cookie_name) == "token-router-test"


def test_auth_login_accepts_form_payload():
    client = get_client()
    client.app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    try:
        response = client.post("/auth/login", data={"rut": "12.345.678-5"})
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["rut_ingresado"] == "12.345.678-5"
    assert response.json()["status"] == "session_created"
