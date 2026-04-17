"""Pruebas del servicio de creacion de actividades."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time

from backend.modulos.actividades.servicios import (
    ActividadCreateCommand,
    ActividadCreateFormQuery,
    ActividadCreateService,
    ActivityCreationPermissionDeniedError,
    ActivityCreationValidationError,
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


@dataclass
class _FakeActividad:
    id_actividad: int
    titulo: str


class StubActividadRepository:
    def __init__(self) -> None:
        self.last_payload: dict[str, object] | None = None

    def create(self, **kwargs):
        self.last_payload = kwargs
        return _FakeActividad(id_actividad=77, titulo=str(kwargs["titulo"]))


class StubUsuarioRepository:
    def __init__(self) -> None:
        self._usuarios = {
            1: _FakeUsuario(1, "Administrador", "12.345.678-5"),
            2: _FakeUsuario(2, "Usuario Abril", "11.111.111-1"),
            3: _FakeUsuario(3, "Usuario Mayo", "22.222.222-2"),
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


def test_create_service_prepares_regular_user_form_for_self_only():
    service = _build_service()

    view = service.prepare_form(
        ActividadCreateFormQuery(actor_user_id=2, actor_role_id=2)
    )

    assert view.allow_user_selection is False
    assert len(view.usuarios) == 1
    assert view.usuarios[0].value == 2
    assert view.form.id_usuario == "2"
    assert [categoria.label for categoria in view.categorias] == ["Trabajo", "Estudio"]


def test_create_service_persists_valid_regular_user_activity():
    actividad_repository = StubActividadRepository()
    service = _build_service(actividad_repository=actividad_repository)

    result = service.create(
        ActividadCreateCommand(
            actor_user_id=2,
            actor_role_id=2,
            titulo="Ensayo de presentacion",
            descripcion="Repasar la defensa del proyecto.",
            fecha_actividad="2026-04-18",
            hora_inicio="09:00",
            hora_fin="10:00",
            emoji="🎤",
            lugar="Sala 4",
            id_categoria="1",
            id_usuario="2",
            realizada=True,
        )
    )

    assert result.id_actividad == 77
    assert actividad_repository.last_payload is not None
    assert actividad_repository.last_payload["titulo"] == "Ensayo de presentacion"
    assert actividad_repository.last_payload["fecha_actividad"] == date(2026, 4, 18)
    assert actividad_repository.last_payload["hora_inicio"] == time(9, 0)
    assert actividad_repository.last_payload["hora_fin"] == time(10, 0)
    assert actividad_repository.last_payload["id_usuario"] == 2
    assert actividad_repository.last_payload["id_categoria"] == 1
    assert actividad_repository.last_payload["realizada"] is True
    assert isinstance(actividad_repository.last_payload["fecha_creacion"], datetime)


def test_create_service_rejects_activity_outside_april():
    service = _build_service()

    try:
        service.create(
            ActividadCreateCommand(
                actor_user_id=2,
                actor_role_id=2,
                titulo="Actividad invalida",
                descripcion="",
                fecha_actividad="2026-05-02",
                hora_inicio="09:00",
                hora_fin="10:00",
                emoji="",
                lugar="",
                id_categoria="1",
                id_usuario="2",
                realizada=False,
            )
        )
        assert False, "Se esperaba ActivityCreationValidationError"
    except ActivityCreationValidationError as exc:
        assert exc.field_errors["fecha_actividad"] == (
            "Solo se permiten actividades entre el 1 y el 30 de abril."
        )


def test_create_service_rejects_invalid_hour_range():
    service = _build_service()

    try:
        service.create(
            ActividadCreateCommand(
                actor_user_id=2,
                actor_role_id=2,
                titulo="Horario inconsistente",
                descripcion="",
                fecha_actividad="2026-04-08",
                hora_inicio="14:00",
                hora_fin="13:30",
                emoji="",
                lugar="",
                id_categoria="1",
                id_usuario="2",
                realizada=False,
            )
        )
        assert False, "Se esperaba ActivityCreationValidationError"
    except ActivityCreationValidationError as exc:
        assert exc.field_errors["hora_fin"] == (
            "La hora de fin debe ser posterior a la de inicio."
        )


def test_create_service_rejects_regular_user_assigning_foreign_user():
    service = _build_service()

    try:
        service.create(
            ActividadCreateCommand(
                actor_user_id=2,
                actor_role_id=2,
                titulo="Intento invalido",
                descripcion="",
                fecha_actividad="2026-04-09",
                hora_inicio="10:00",
                hora_fin="11:00",
                emoji="",
                lugar="",
                id_categoria="1",
                id_usuario="1",
                realizada=False,
            )
        )
        assert False, "Se esperaba ActivityCreationPermissionDeniedError"
    except ActivityCreationPermissionDeniedError as exc:
        assert str(exc) == (
            "Un usuario comun solo puede crear actividades para si mismo."
        )


def test_create_service_allows_admin_to_assign_any_active_user():
    actividad_repository = StubActividadRepository()
    service = _build_service(actividad_repository=actividad_repository)

    service.create(
        ActividadCreateCommand(
            actor_user_id=1,
            actor_role_id=1,
            titulo="Actividad delegada",
            descripcion="",
            fecha_actividad="2026-04-24",
            hora_inicio="15:00",
            hora_fin="16:00",
            emoji="",
            lugar="Oficina",
            id_categoria="2",
            id_usuario="3",
            realizada=False,
        )
    )

    assert actividad_repository.last_payload is not None
    assert actividad_repository.last_payload["id_usuario"] == 3
    assert actividad_repository.last_payload["id_categoria"] == 2


def _build_service(
    *,
    actividad_repository: StubActividadRepository | None = None,
) -> ActividadCreateService:
    return ActividadCreateService(
        actividad_repository or StubActividadRepository(),
        StubUsuarioRepository(),
        StubCategoriaRepository(),
        april_month=4,
    )
