"""Pruebas del servicio inicial de auth."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from backend.modulos.auth.servicios.login_service import AuthService


@dataclass
class FakeUser:
    id_usuario: int = 1
    nombre: str = "Administrador"
    rut: str = "12.345.678-5"
    id_rol: int = 1
    tema_preferido: str | None = "light"
    activo: bool = True


@dataclass
class FakeSession:
    id_sesion: int = 101
    id_usuario: int = 1
    token_sesion: str = "token-de-prueba"
    fecha_inicio: datetime = datetime(2026, 4, 15, 10, 0, 0)
    ultimo_movimiento: datetime = datetime(2026, 4, 15, 10, 0, 0)
    activa: bool = True


class StubUsuarioRepository:
    def __init__(self, user: FakeUser | None = None) -> None:
        self._user = user
        self.received_rut: str | None = None

    def get_by_rut(self, rut: str) -> FakeUser | None:
        self.received_rut = rut
        return self._user


class StubSesionService:
    def __init__(self) -> None:
        self.created_for_user_id: int | None = None
        self.session = FakeSession()

    def create_session_for_user(self, id_usuario: int) -> FakeSession:
        self.created_for_user_id = id_usuario
        self.session.id_usuario = id_usuario
        return self.session


def test_prepare_login_returns_validation_error_for_invalid_rut():
    repository = StubUsuarioRepository()
    session_service = StubSesionService()
    service = AuthService(repository, session_service)

    result = service.prepare_login("12.345.678-9")

    assert result.http_status == 400
    assert result.response.status == "validation_error"
    assert result.response.siguiente_paso == "corregir_rut"
    assert result.session_cookie_token is None


def test_prepare_login_returns_access_denied_for_valid_but_unknown_rut():
    repository = StubUsuarioRepository()
    session_service = StubSesionService()
    service = AuthService(repository, session_service)

    result = service.prepare_login("12.345.678-5")

    assert repository.received_rut == "12345678-5"
    assert result.http_status == 403
    assert result.response.status == "access_denied"
    assert result.response.usuario_existe is False
    assert result.response.siguiente_paso == "acceso_denegado"
    assert result.session_cookie_token is None


def test_prepare_login_creates_session_for_existing_user():
    repository = StubUsuarioRepository(user=FakeUser())
    session_service = StubSesionService()
    service = AuthService(repository, session_service)

    result = service.prepare_login("12.345.678-5")

    assert result.http_status == 200
    assert result.response.status == "session_created"
    assert result.response.usuario_existe is True
    assert result.response.usuario is not None
    assert result.response.usuario.nombre == "Administrador"
    assert result.response.sesion is not None
    assert result.response.sesion.id_sesion == 101
    assert result.response.siguiente_paso == "validar_sesion_activa"
    assert session_service.created_for_user_id == 1
    assert result.session_cookie_token == "token-de-prueba"
