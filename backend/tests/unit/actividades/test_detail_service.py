"""Pruebas del servicio de detalle de actividad."""

from __future__ import annotations

from datetime import datetime, time, date

from backend.modulos.actividades.servicios import (
    ActividadDetailQuery,
    ActividadDetailService,
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
)


class StubDetailRepository:
    def __init__(self, actividad: _FakeActividad | None) -> None:
        self.actividad = actividad

    def get_by_id(self, actividad_id: int):
        if self.actividad is None:
            return None
        if self.actividad.id_actividad != actividad_id:
            return None
        return self.actividad


class _FakeCategoria:
    def __init__(self, nombre_categoria: str, descripcion: str | None) -> None:
        self.nombre_categoria = nombre_categoria
        self.descripcion = descripcion


class _FakeUsuario:
    def __init__(self, nombre: str, rut: str) -> None:
        self.nombre = nombre
        self.rut = rut


class _FakeActividad:
    def __init__(
        self,
        *,
        id_actividad: int,
        id_usuario: int,
        realizada: bool,
    ) -> None:
        self.id_actividad = id_actividad
        self.titulo = "Reunion general"
        self.descripcion = "Revision semanal del proyecto."
        self.fecha_actividad = date(2026, 4, 10)
        self.hora_inicio = time(9, 0)
        self.hora_fin = time(10, 0)
        self.emoji = "📌"
        self.realizada = realizada
        self.lugar = "Sala 1"
        self.id_usuario = id_usuario
        self.fecha_creacion = datetime(2026, 4, 5, 10, 0, 0)
        self.categoria = _FakeCategoria("Trabajo", "Tareas laborales")
        self.usuario = _FakeUsuario("Administrador", "12.345.678-5")


def test_detail_service_returns_activity_for_owner():
    repository = StubDetailRepository(
        _FakeActividad(id_actividad=1, id_usuario=2, realizada=False)
    )
    service = ActividadDetailService(repository)

    result = service.get_detail(
        ActividadDetailQuery(
            actividad_id=1,
            actor_user_id=2,
            actor_role_id=2,
        )
    )

    assert result.id_actividad == 1
    assert result.titulo == "Reunion general"
    assert result.categoria_nombre == "Trabajo"
    assert result.usuario_nombre == "Administrador"


def test_detail_service_allows_admin_to_view_any_activity():
    repository = StubDetailRepository(
        _FakeActividad(id_actividad=1, id_usuario=2, realizada=True)
    )
    service = ActividadDetailService(repository)

    result = service.get_detail(
        ActividadDetailQuery(
            actividad_id=1,
            actor_user_id=1,
            actor_role_id=1,
        )
    )

    assert result.realizada is True


def test_detail_service_rejects_regular_user_on_foreign_activity():
    repository = StubDetailRepository(
        _FakeActividad(id_actividad=1, id_usuario=1, realizada=False)
    )
    service = ActividadDetailService(repository)

    try:
        service.get_detail(
            ActividadDetailQuery(
                actividad_id=1,
                actor_user_id=2,
                actor_role_id=2,
            )
        )
        assert False, "Se esperaba ActivityPermissionDeniedError"
    except ActivityPermissionDeniedError:
        assert True


def test_detail_service_raises_when_activity_does_not_exist():
    service = ActividadDetailService(StubDetailRepository(None))

    try:
        service.get_detail(
            ActividadDetailQuery(
                actividad_id=999,
                actor_user_id=1,
                actor_role_id=1,
            )
        )
        assert False, "Se esperaba ActivityNotFoundError"
    except ActivityNotFoundError:
        assert True
