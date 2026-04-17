"""Pruebas del servicio de checklist de actividades."""

from __future__ import annotations

from backend.modulos.actividades.servicios import (
    ActividadChecklistCommand,
    ActividadChecklistService,
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
)


class StubChecklistRepository:
    def __init__(self, actividad: _FakeActividad | None) -> None:
        self.actividad = actividad
        self.updated_to: bool | None = None

    def get_by_id(self, actividad_id: int):
        if self.actividad is None:
            return None
        if self.actividad.id_actividad != actividad_id:
            return None
        return self.actividad

    def update_realizada(self, actividad, *, realizada: bool):
        self.updated_to = realizada
        actividad.realizada = realizada
        return actividad


class _FakeActividad:
    def __init__(self, *, id_actividad: int, id_usuario: int, realizada: bool) -> None:
        self.id_actividad = id_actividad
        self.id_usuario = id_usuario
        self.realizada = realizada


def test_checklist_service_allows_regular_user_on_own_activity():
    repository = StubChecklistRepository(
        _FakeActividad(id_actividad=8, id_usuario=2, realizada=False)
    )
    service = ActividadChecklistService(repository)

    actividad = service.set_realizada(
        ActividadChecklistCommand(
            actividad_id=8,
            actor_user_id=2,
            actor_role_id=2,
            realizada=True,
        )
    )

    assert actividad.realizada is True
    assert repository.updated_to is True


def test_checklist_service_rejects_regular_user_on_foreign_activity():
    repository = StubChecklistRepository(
        _FakeActividad(id_actividad=8, id_usuario=1, realizada=False)
    )
    service = ActividadChecklistService(repository)

    try:
        service.set_realizada(
            ActividadChecklistCommand(
                actividad_id=8,
                actor_user_id=2,
                actor_role_id=2,
                realizada=True,
            )
        )
        assert False, "Se esperaba ActivityPermissionDeniedError"
    except ActivityPermissionDeniedError:
        assert repository.updated_to is None


def test_checklist_service_allows_admin_on_any_activity():
    repository = StubChecklistRepository(
        _FakeActividad(id_actividad=8, id_usuario=2, realizada=False)
    )
    service = ActividadChecklistService(repository)

    actividad = service.set_realizada(
        ActividadChecklistCommand(
            actividad_id=8,
            actor_user_id=1,
            actor_role_id=1,
            realizada=True,
        )
    )

    assert actividad.realizada is True
    assert repository.updated_to is True


def test_checklist_service_raises_when_activity_does_not_exist():
    repository = StubChecklistRepository(None)
    service = ActividadChecklistService(repository)

    try:
        service.set_realizada(
            ActividadChecklistCommand(
                actividad_id=404,
                actor_user_id=1,
                actor_role_id=1,
                realizada=True,
            )
        )
        assert False, "Se esperaba ActivityNotFoundError"
    except ActivityNotFoundError:
        assert repository.updated_to is None
