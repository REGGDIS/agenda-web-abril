"""Pruebas del servicio de edicion de actividades."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time

from backend.modulos.actividades.servicios import (
    ActividadEditCommand,
    ActividadEditQuery,
    ActividadEditService,
    ActivityEditionValidationError,
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
)


@dataclass
class _FakeUsuario:
    id_usuario: int
    nombre: str
    rut: str
    activo: bool = True


@dataclass
class _FakeCategoria:
    id_categoria: int
    nombre_categoria: str


class _FakeActividad:
    def __init__(
        self,
        *,
        id_actividad: int,
        id_usuario: int,
        id_categoria: int = 1,
        realizada: bool = False,
    ) -> None:
        self.id_actividad = id_actividad
        self.titulo = "Reunion general"
        self.descripcion = "Revision semanal"
        self.fecha_actividad = date(2026, 4, 10)
        self.hora_inicio = time(9, 0)
        self.hora_fin = time(10, 0)
        self.emoji = "📌"
        self.realizada = realizada
        self.lugar = "Sala 1"
        self.id_usuario = id_usuario
        self.id_categoria = id_categoria


class StubActividadRepository:
    def __init__(self, actividad: _FakeActividad | None = None) -> None:
        self.actividad = actividad or _FakeActividad(id_actividad=5, id_usuario=2)
        self.last_payload: dict[str, object] | None = None

    def get_by_id(self, actividad_id: int):
        if self.actividad is None or self.actividad.id_actividad != actividad_id:
            return None
        return self.actividad

    def update(self, actividad, **kwargs):
        self.last_payload = kwargs
        for key, value in kwargs.items():
            setattr(actividad, key, value)
        return actividad


class StubUsuarioRepository:
    def __init__(self) -> None:
        self._usuarios = {
            1: _FakeUsuario(1, "Administrador", "12.345.678-5"),
            2: _FakeUsuario(2, "Usuario Abril", "11.111.111-1"),
            3: _FakeUsuario(3, "Usuario Dos", "22.222.222-2"),
        }

    def get_by_id(self, user_id: int):
        return self._usuarios.get(user_id)

    def list_active_users(self):
        return list(self._usuarios.values())


class StubCategoriaRepository:
    def __init__(self) -> None:
        self._categorias = {
            1: _FakeCategoria(1, "Trabajo"),
            2: _FakeCategoria(2, "Estudio"),
        }

    def get_by_id(self, categoria_id: int):
        return self._categorias.get(categoria_id)

    def list_all(self):
        return list(self._categorias.values())


def test_edit_service_preloads_current_activity_data():
    service = _build_service()

    view = service.prepare_form(
        ActividadEditQuery(actividad_id=5, actor_user_id=2, actor_role_id=2)
    )

    assert view.form.titulo == "Reunion general"
    assert view.form.fecha_actividad == "2026-04-10"
    assert view.form.hora_inicio == "09:00"
    assert view.form.id_usuario == "2"
    assert view.allow_user_selection is False


def test_edit_service_updates_owned_activity():
    actividad_repository = StubActividadRepository()
    service = _build_service(actividad_repository=actividad_repository)

    result = service.update(
        ActividadEditCommand(
            actividad_id=5,
            actor_user_id=2,
            actor_role_id=2,
            titulo="Reunion ajustada",
            descripcion="Nueva descripcion",
            fecha_actividad="2026-04-11",
            hora_inicio="11:00",
            hora_fin="12:00",
            emoji="📝",
            lugar="Sala 2",
            id_categoria="2",
            id_usuario="2",
            realizada=True,
        )
    )

    assert result.id_actividad == 5
    assert actividad_repository.last_payload is not None
    assert actividad_repository.last_payload["titulo"] == "Reunion ajustada"
    assert actividad_repository.last_payload["fecha_actividad"] == date(2026, 4, 11)
    assert actividad_repository.last_payload["hora_inicio"] == time(11, 0)
    assert actividad_repository.last_payload["hora_fin"] == time(12, 0)
    assert actividad_repository.last_payload["id_categoria"] == 2
    assert actividad_repository.last_payload["id_usuario"] == 2
    assert actividad_repository.last_payload["realizada"] is True


def test_edit_service_allows_admin_to_reassign_activity():
    actividad_repository = StubActividadRepository()
    service = _build_service(actividad_repository=actividad_repository)

    service.update(
        ActividadEditCommand(
            actividad_id=5,
            actor_user_id=1,
            actor_role_id=1,
            titulo="Actividad administrada",
            descripcion="",
            fecha_actividad="2026-04-15",
            hora_inicio="08:30",
            hora_fin="09:30",
            emoji="",
            lugar="Oficina",
            id_categoria="1",
            id_usuario="3",
            realizada=False,
        )
    )

    assert actividad_repository.last_payload is not None
    assert actividad_repository.last_payload["id_usuario"] == 3


def test_edit_service_rejects_regular_user_editing_foreign_activity():
    actividad_repository = StubActividadRepository(
        actividad=_FakeActividad(id_actividad=5, id_usuario=1)
    )
    service = _build_service(actividad_repository=actividad_repository)

    try:
        service.prepare_form(
            ActividadEditQuery(actividad_id=5, actor_user_id=2, actor_role_id=2)
        )
        assert False, "Se esperaba ActivityPermissionDeniedError"
    except ActivityPermissionDeniedError as exc:
        assert str(exc) == "El usuario no tiene permisos para editar esta actividad."


def test_edit_service_rejects_activity_outside_april():
    service = _build_service()

    try:
        service.update(
            ActividadEditCommand(
                actividad_id=5,
                actor_user_id=2,
                actor_role_id=2,
                titulo="Cambio invalido",
                descripcion="",
                fecha_actividad="2026-05-01",
                hora_inicio="09:00",
                hora_fin="10:00",
                emoji="",
                lugar="",
                id_categoria="1",
                id_usuario="2",
                realizada=False,
            )
        )
        assert False, "Se esperaba ActivityEditionValidationError"
    except ActivityEditionValidationError as exc:
        assert exc.field_errors["fecha_actividad"] == (
            "Solo se permiten actividades entre el 1 y el 30 de abril."
        )


def test_edit_service_rejects_invalid_hour_range():
    service = _build_service()

    try:
        service.update(
            ActividadEditCommand(
                actividad_id=5,
                actor_user_id=2,
                actor_role_id=2,
                titulo="Cambio invalido",
                descripcion="",
                fecha_actividad="2026-04-12",
                hora_inicio="11:00",
                hora_fin="10:00",
                emoji="",
                lugar="",
                id_categoria="1",
                id_usuario="2",
                realizada=False,
            )
        )
        assert False, "Se esperaba ActivityEditionValidationError"
    except ActivityEditionValidationError as exc:
        assert exc.field_errors["hora_fin"] == (
            "La hora de fin debe ser posterior a la de inicio."
        )


def test_edit_service_raises_not_found_for_unknown_activity():
    actividad_repository = StubActividadRepository()
    actividad_repository.actividad = None
    service = _build_service(actividad_repository=actividad_repository)

    try:
        service.prepare_form(
            ActividadEditQuery(actividad_id=999, actor_user_id=1, actor_role_id=1)
        )
        assert False, "Se esperaba ActivityNotFoundError"
    except ActivityNotFoundError as exc:
        assert str(exc) == "No existe actividad con id 999."


def _build_service(
    *,
    actividad_repository: StubActividadRepository | None = None,
) -> ActividadEditService:
    return ActividadEditService(
        actividad_repository or StubActividadRepository(),
        StubUsuarioRepository(),
        StubCategoriaRepository(),
        april_month=4,
    )
