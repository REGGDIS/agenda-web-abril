"""Pruebas de la dependencia que resuelve la sesion actual."""

from __future__ import annotations

from datetime import datetime

from starlette.requests import Request

from backend.app.config.settings import get_settings
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult


class FakeSesionService:
    def __init__(self) -> None:
        self.last_operation: str | None = None
        self.received_token: str | None = None

    def resolve_session_from_token(
        self,
        token_sesion: str | None,
    ) -> SesionResolutionResult:
        self.last_operation = "resolve"
        self.received_token = token_sesion
        return _build_valid_result()

    def register_activity_from_token(
        self,
        token_sesion: str | None,
    ) -> SesionResolutionResult:
        self.last_operation = "activity"
        self.received_token = token_sesion
        return _build_valid_result()


def test_dependency_registers_activity_for_protected_calendar_request():
    request = _build_request("/calendario")
    service = FakeSesionService()

    result = get_current_session_result(request, service)

    assert result.response.status == "session_valid"
    assert service.last_operation == "activity"
    assert service.received_token == "token-de-prueba"


def test_dependency_registers_activity_for_protected_activity_submit():
    request = _build_request("/actividades/nueva", method="POST")
    service = FakeSesionService()

    result = get_current_session_result(request, service)

    assert result.response.status == "session_valid"
    assert service.last_operation == "activity"
    assert service.received_token == "token-de-prueba"


def test_dependency_only_resolves_session_for_session_routes():
    request = _build_request("/sesiones/actual")
    service = FakeSesionService()

    result = get_current_session_result(request, service)

    assert result.response.status == "session_valid"
    assert service.last_operation == "resolve"
    assert service.received_token == "token-de-prueba"


def _build_request(path: str, method: str = "GET") -> Request:
    settings = get_settings()
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": [
            (b"host", b"testserver"),
            (
                b"cookie",
                f"{settings.session_cookie_name}=token-de-prueba".encode("ascii"),
            ),
        ],
        "scheme": "http",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
    }
    return Request(scope)


def _build_valid_result() -> SesionResolutionResult:
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
            ultimo_movimiento_anterior=datetime(2026, 4, 19, 12, 0, 0),
            sesion={
                "id_sesion": 4,
                "id_usuario": 2,
                "fecha_inicio": datetime(2026, 4, 19, 11, 0, 0),
                "ultimo_movimiento": datetime(2026, 4, 19, 12, 0, 30),
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
