"""Pruebas del servicio de eliminacion de actividades."""

from __future__ import annotations

from datetime import date, time

from backend.modulos.actividades.servicios import (
    ActividadDeleteCommand,
    ActividadDeleteQuery,
    ActividadDeleteService,
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
)


class _FakeCategoria:
    def __init__(self, nombre_categoria: str) -> None:
        self.nombre_categoria = nombre_categoria


class _FakeUsuario:
    def __init__(self, nombre: str) -> None:
        self.nombre = nombre


class _FakeActividad:
    def __init__(self, *, id_actividad: int, id_usuario: int) -> None:
        self.id_actividad = id_actividad
        self.titulo = "Reunion general"
        self.descripcion = "Revision semanal"
        self.fecha_actividad = date(2026, 4, 10)
        self.hora_inicio = time(9, 0)
        self.hora_fin = time(10, 0)
        self.id_usuario = id_usuario
        self.categoria = _FakeCategoria("Trabajo")
        self.usuario = _FakeUsuario("Usuario Abril")


class StubDeleteRepository:
    def __init__(self, actividad: _FakeActividad | None) -> None:
        self.actividad = actividad
        self.deleted_activity_id: int | None = None

    def get_by_id(self, actividad_id: int):
        if self.actividad is None or self.actividad.id_actividad != actividad_id:
            return None
        return self.actividad

    def delete(self, actividad) -> None:
        self.deleted_activity_id = actividad.id_actividad
        self.actividad = None


def test_delete_service_builds_confirmation_preview():
    service = ActividadDeleteService(
        StubDeleteRepository(_FakeActividad(id_actividad=5, id_usuario=2))
    )

    preview = service.get_preview(
        ActividadDeleteQuery(actividad_id=5, actor_user_id=2, actor_role_id=2)
    )

    assert preview.id_actividad == 5
    assert preview.titulo == "Reunion general"
    assert preview.fecha_actividad_label == "10/04/2026"
    assert preview.horario_label == "09:00 - 10:00"
    assert preview.categoria_nombre == "Trabajo"
    assert preview.usuario_nombre == "Usuario Abril"


def test_delete_service_deletes_owned_activity():
    repository = StubDeleteRepository(_FakeActividad(id_actividad=5, id_usuario=2))
    service = ActividadDeleteService(repository)

    service.delete(
        ActividadDeleteCommand(actividad_id=5, actor_user_id=2, actor_role_id=2)
    )

    assert repository.deleted_activity_id == 5
    assert repository.actividad is None


def test_delete_service_allows_admin_to_delete_foreign_activity():
    repository = StubDeleteRepository(_FakeActividad(id_actividad=5, id_usuario=2))
    service = ActividadDeleteService(repository)

    service.delete(
        ActividadDeleteCommand(actividad_id=5, actor_user_id=1, actor_role_id=1)
    )

    assert repository.deleted_activity_id == 5


def test_delete_service_rejects_regular_user_on_foreign_activity():
    service = ActividadDeleteService(
        StubDeleteRepository(_FakeActividad(id_actividad=5, id_usuario=1))
    )

    try:
        service.get_preview(
            ActividadDeleteQuery(actividad_id=5, actor_user_id=2, actor_role_id=2)
        )
        assert False, "Se esperaba ActivityPermissionDeniedError"
    except ActivityPermissionDeniedError as exc:
        assert str(exc) == "El usuario no tiene permisos para eliminar esta actividad."


def test_delete_service_raises_not_found_for_missing_activity():
    service = ActividadDeleteService(StubDeleteRepository(None))

    try:
        service.delete(
            ActividadDeleteCommand(actividad_id=999, actor_user_id=1, actor_role_id=1)
        )
        assert False, "Se esperaba ActivityNotFoundError"
    except ActivityNotFoundError as exc:
        assert str(exc) == "No existe actividad con id 999."
