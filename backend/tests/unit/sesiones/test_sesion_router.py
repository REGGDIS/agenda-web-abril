"""Pruebas de la ruta de sesion actual."""

from __future__ import annotations

from datetime import datetime

from backend.app.config.settings import get_settings
from backend.modulos.sesiones.servicios import (
    SesionResolutionResult,
    get_sesion_service,
)
from backend.tests.conftest import get_client


class FakeSesionService:
    def __init__(self) -> None:
        self.received_token: str | None = None

    def resolve_session_from_token(self, token_sesion: str | None) -> SesionResolutionResult:
        self.received_token = token_sesion
        if token_sesion == "token-valido":
            return SesionResolutionResult(
                http_status=200,
                response={
                    "success": True,
                    "status": "session_valid",
                    "message": "Sesion valida.",
                    "cookie_present": True,
                    "session_found": True,
                    "session_active": True,
                    "ultimo_movimiento_actualizado": True,
                    "ultimo_movimiento_anterior": datetime(2026, 4, 15, 10, 0, 0),
                    "sesion": {
                        "id_sesion": 9,
                        "id_usuario": 1,
                        "fecha_inicio": datetime(2026, 4, 15, 9, 59, 0),
                        "ultimo_movimiento": datetime(2026, 4, 15, 10, 1, 0),
                        "fecha_cierre": None,
                        "activa": True,
                    },
                    "usuario": {
                        "id_usuario": 1,
                        "nombre": "Administrador",
                        "rut": "12.345.678-5",
                        "id_rol": 1,
                        "tema_preferido": "light",
                        "activo": True,
                    },
                },
            )

        return SesionResolutionResult(
            http_status=401,
            response={
                "success": False,
                "status": "session_not_found",
                "message": "Sesion no encontrada.",
                "cookie_present": True,
                "session_found": False,
                "session_active": False,
                "ultimo_movimiento_actualizado": False,
                "ultimo_movimiento_anterior": None,
                "sesion": None,
                "usuario": None,
            },
        )


def test_current_session_route_returns_cookie_missing_without_cookie():
    client = get_client()

    response = client.get("/sesiones/actual")

    assert response.status_code == 401
    assert response.json()["status"] == "cookie_missing"


def test_current_session_route_reads_cookie_and_returns_valid_session():
    client = get_client()
    fake_service = FakeSesionService()
    client.app.dependency_overrides[get_sesion_service] = lambda: fake_service
    client.cookies.set(get_settings().session_cookie_name, "token-valido")

    try:
        response = client.get("/sesiones/actual")
    finally:
        client.app.dependency_overrides.clear()
        client.cookies.clear()

    assert response.status_code == 200
    assert fake_service.received_token == "token-valido"
    assert response.json()["status"] == "session_valid"
    assert response.json()["usuario"]["nombre"] == "Administrador"
