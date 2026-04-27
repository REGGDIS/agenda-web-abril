"""Pruebas de la ruta JSON de categorias."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from backend.modulos.categorias.rutas.router import get_categoria_repository
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult
from backend.tests.conftest import get_client


@dataclass
class _FakeCategoria:
    id_categoria: int
    nombre_categoria: str


class FakeCategoriaRepository:
    def list_all(self):
        return [
            _FakeCategoria(2, "Estudio"),
            _FakeCategoria(1, "Trabajo"),
        ]


def test_categorias_json_returns_real_category_options():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _valid_session_result
    client.app.dependency_overrides[get_categoria_repository] = (
        lambda: FakeCategoriaRepository()
    )

    try:
        response = client.get("/categorias")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "categorias": [
            {"id_categoria": 2, "nombre_categoria": "Estudio"},
            {"id_categoria": 1, "nombre_categoria": "Trabajo"},
        ],
    }


def test_categorias_json_returns_error_when_session_is_invalid():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = _invalid_session_result

    try:
        response = client.get("/categorias")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["categorias"] == []
    assert response.json()["message"] == "Sin cookie."


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
