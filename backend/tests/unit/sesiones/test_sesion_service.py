"""Pruebas del servicio de sesiones."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from backend.modulos.sesiones.servicios import SesionService


@dataclass
class FakeUser:
    id_usuario: int
    nombre: str
    rut: str
    id_rol: int
    tema_preferido: str | None
    activo: bool


@dataclass
class FakeSesion:
    id_sesion: int
    id_usuario: int
    token_sesion: str
    fecha_inicio: datetime
    ultimo_movimiento: datetime
    fecha_cierre: datetime | None
    activa: bool
    usuario: FakeUser | None = None


class StubSesionRepository:
    def __init__(self) -> None:
        self.created_payload: dict[str, object] | None = None
        self.session_by_token: FakeSesion | None = None
        self.touched_at: datetime | None = None
        self.closed_at: datetime | None = None

    def create(self, **kwargs) -> FakeSesion:
        self.created_payload = kwargs
        return FakeSesion(
            id_sesion=1,
            id_usuario=int(kwargs["id_usuario"]),
            token_sesion=str(kwargs["token_sesion"]),
            fecha_inicio=kwargs["fecha_inicio"],
            ultimo_movimiento=kwargs["ultimo_movimiento"],
            fecha_cierre=None,
            activa=True,
        )

    def get_active_by_token(self, token_sesion: str) -> FakeSesion | None:
        if self.session_by_token and self.session_by_token.activa:
            return self.session_by_token
        return None

    def get_by_token(self, token_sesion: str) -> FakeSesion | None:
        return self.session_by_token

    def touch_last_movement(
        self,
        sesion: FakeSesion,
        *,
        ultimo_movimiento: datetime,
    ) -> FakeSesion:
        self.touched_at = ultimo_movimiento
        sesion.ultimo_movimiento = ultimo_movimiento
        return sesion

    def close_session(
        self,
        sesion: FakeSesion,
        *,
        fecha_cierre: datetime,
    ) -> FakeSesion:
        self.closed_at = fecha_cierre
        sesion.fecha_cierre = fecha_cierre
        sesion.activa = False
        return sesion


def test_create_session_for_user_generates_token_and_dates():
    repository = StubSesionRepository()
    service = SesionService(repository, session_inactivity_minutes=1)

    session = service.create_session_for_user(3)

    assert repository.created_payload is not None
    assert repository.created_payload["id_usuario"] == 3
    assert isinstance(repository.created_payload["token_sesion"], str)
    assert len(repository.created_payload["token_sesion"]) >= 32
    assert session.id_usuario == 3
    assert session.activa is True


def test_resolve_session_from_token_returns_cookie_missing_when_absent():
    repository = StubSesionRepository()
    service = SesionService(repository, session_inactivity_minutes=1)

    result = service.resolve_session_from_token(None)

    assert result.http_status == 401
    assert result.response.status == "cookie_missing"
    assert result.response.cookie_present is False
    assert result.response.ultimo_movimiento_actualizado is False


def test_resolve_session_from_token_returns_inactive_when_session_is_disabled():
    repository = StubSesionRepository()
    repository.session_by_token = FakeSesion(
        id_sesion=10,
        id_usuario=2,
        token_sesion="token-inactivo",
        fecha_inicio=datetime(2026, 4, 15, 9, 0, 0),
        ultimo_movimiento=datetime(2026, 4, 15, 9, 30, 0),
        fecha_cierre=datetime(2026, 4, 15, 9, 31, 0),
        activa=False,
        usuario=FakeUser(
            id_usuario=2,
            nombre="Usuario Inactivo",
            rut="11.111.111-1",
            id_rol=2,
            tema_preferido="light",
            activo=True,
        ),
    )
    service = SesionService(repository, session_inactivity_minutes=1)

    result = service.resolve_session_from_token("token-inactivo")

    assert result.http_status == 403
    assert result.response.status == "session_inactive"
    assert result.response.session_found is True
    assert result.response.session_active is False
    assert result.response.usuario is not None
    assert result.response.usuario.nombre == "Usuario Inactivo"


def test_resolve_session_from_token_does_not_update_last_movement_for_valid_session():
    now = datetime.now()
    repository = StubSesionRepository()
    repository.session_by_token = FakeSesion(
        id_sesion=5,
        id_usuario=2,
        token_sesion="token-ok",
        fecha_inicio=now - timedelta(minutes=1),
        ultimo_movimiento=now - timedelta(seconds=10),
        fecha_cierre=None,
        activa=True,
        usuario=FakeUser(
            id_usuario=2,
            nombre="Usuario Abril",
            rut="11.111.111-1",
            id_rol=2,
            tema_preferido="light",
            activo=True,
        ),
    )
    service = SesionService(repository, session_inactivity_minutes=1)

    result = service.resolve_session_from_token("token-ok")

    assert result.http_status == 200
    assert result.response.status == "session_valid"
    assert result.response.ultimo_movimiento_actualizado is False
    assert result.response.ultimo_movimiento_anterior is None
    assert repository.touched_at is None
    assert result.response.sesion is not None
    assert result.response.usuario is not None
    assert result.response.usuario.nombre == "Usuario Abril"


def test_register_activity_from_token_updates_last_movement_for_valid_session():
    now = datetime.now()
    previous_last_movement = now - timedelta(seconds=10)
    repository = StubSesionRepository()
    repository.session_by_token = FakeSesion(
        id_sesion=5,
        id_usuario=2,
        token_sesion="token-ok",
        fecha_inicio=now - timedelta(minutes=1),
        ultimo_movimiento=previous_last_movement,
        fecha_cierre=None,
        activa=True,
        usuario=FakeUser(
            id_usuario=2,
            nombre="Usuario Abril",
            rut="11.111.111-1",
            id_rol=2,
            tema_preferido="light",
            activo=True,
        ),
    )
    service = SesionService(repository, session_inactivity_minutes=1)

    result = service.register_activity_from_token("token-ok")

    assert result.http_status == 200
    assert result.response.status == "session_valid"
    assert result.response.ultimo_movimiento_actualizado is True
    assert result.response.ultimo_movimiento_anterior == previous_last_movement
    assert repository.touched_at is not None


def test_resolve_session_from_token_closes_expired_session():
    now = datetime.now()
    repository = StubSesionRepository()
    repository.session_by_token = FakeSesion(
        id_sesion=8,
        id_usuario=2,
        token_sesion="token-expirado",
        fecha_inicio=now - timedelta(minutes=5),
        ultimo_movimiento=now - timedelta(minutes=2),
        fecha_cierre=None,
        activa=True,
        usuario=FakeUser(
            id_usuario=2,
            nombre="Usuario Abril",
            rut="11.111.111-1",
            id_rol=2,
            tema_preferido="light",
            activo=True,
        ),
    )
    service = SesionService(repository, session_inactivity_minutes=1)

    result = service.resolve_session_from_token("token-expirado")

    assert result.http_status == 401
    assert result.response.status == "session_expired"
    assert result.response.session_active is False
    assert repository.closed_at is not None


def test_expire_session_from_token_closes_active_session():
    now = datetime.now()
    repository = StubSesionRepository()
    repository.session_by_token = FakeSesion(
        id_sesion=11,
        id_usuario=3,
        token_sesion="token-activo",
        fecha_inicio=now - timedelta(minutes=5),
        ultimo_movimiento=now - timedelta(seconds=30),
        fecha_cierre=None,
        activa=True,
        usuario=FakeUser(
            id_usuario=3,
            nombre="Usuario Cierre",
            rut="22.222.222-2",
            id_rol=2,
            tema_preferido="dark",
            activo=True,
        ),
    )
    service = SesionService(repository, session_inactivity_minutes=1)

    result = service.expire_session_from_token("token-activo")

    assert result.http_status == 401
    assert result.response.status == "session_expired"
    assert repository.closed_at is not None
