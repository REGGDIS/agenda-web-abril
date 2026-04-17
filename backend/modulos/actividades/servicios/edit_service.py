"""Servicio para preparar y persistir la edicion de actividades."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Protocol

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings
from backend.app.db.session import get_db
from backend.modulos.actividades.esquemas import (
    ActividadCreateFormData,
    ActividadCreateOptionData,
    ActividadCreateViewData,
    ActividadUpdateResult,
)
from backend.modulos.actividades.modelos import Actividad
from backend.modulos.actividades.repositorios import SqlAlchemyActividadRepository
from backend.modulos.actividades.servicios.calendario_service import ADMIN_ROLE_ID
from backend.modulos.actividades.servicios.checklist_service import (
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
)
from backend.modulos.categorias.modelos import Categoria
from backend.modulos.categorias.repositorios import SqlAlchemyCategoriaRepository
from backend.modulos.usuarios.modelos import Usuario
from backend.modulos.usuarios.repositorios import SqlAlchemyUsuarioRepository


class ActivityEditionValidationError(Exception):
    """Se lanza cuando los datos editados no cumplen las reglas del proyecto."""

    def __init__(
        self,
        *,
        field_errors: dict[str, str],
        general_error: str = "Revisa los datos obligatorios del formulario.",
    ) -> None:
        super().__init__(general_error)
        self.field_errors = field_errors
        self.general_error = general_error


class ActividadEditRepository(Protocol):
    """Contrato minimo para leer y actualizar una actividad."""

    def get_by_id(self, actividad_id: int) -> Actividad | None:
        """Busca una actividad por identificador."""

    def update(
        self,
        actividad: Actividad,
        *,
        titulo: str,
        descripcion: str | None,
        fecha_actividad: date,
        hora_inicio: time,
        hora_fin: time,
        emoji: str | None,
        realizada: bool,
        lugar: str | None,
        id_usuario: int,
        id_categoria: int,
    ) -> Actividad:
        """Persiste la edicion de una actividad."""


class UsuarioEditRepository(Protocol):
    """Contrato minimo para resolver usuarios asignables en edicion."""

    def get_by_id(self, user_id: int) -> Usuario | None:
        """Busca un usuario por identificador."""

    def list_active_users(self) -> list[Usuario]:
        """Obtiene los usuarios activos visibles para reasignacion."""


class CategoriaEditRepository(Protocol):
    """Contrato minimo para resolver categorias editables."""

    def get_by_id(self, categoria_id: int) -> Categoria | None:
        """Busca una categoria por identificador."""

    def list_all(self) -> list[Categoria]:
        """Obtiene todas las categorias registradas."""


@dataclass(frozen=True)
class ActividadEditQuery:
    """Datos necesarios para cargar el formulario de edicion."""

    actividad_id: int
    actor_user_id: int
    actor_role_id: int

    @property
    def actor_is_admin(self) -> bool:
        return self.actor_role_id == ADMIN_ROLE_ID


@dataclass(frozen=True)
class ActividadEditCommand:
    """Datos crudos enviados desde el formulario de edicion."""

    actividad_id: int
    actor_user_id: int
    actor_role_id: int
    titulo: str
    descripcion: str
    fecha_actividad: str
    hora_inicio: str
    hora_fin: str
    emoji: str
    lugar: str
    id_categoria: str
    id_usuario: str
    realizada: bool

    @property
    def actor_is_admin(self) -> bool:
        return self.actor_role_id == ADMIN_ROLE_ID


class ActividadEditService:
    """Coordina permisos, precarga y persistencia de la edicion."""

    def __init__(
        self,
        actividad_repository: ActividadEditRepository,
        usuario_repository: UsuarioEditRepository,
        categoria_repository: CategoriaEditRepository,
        *,
        april_month: int,
    ) -> None:
        self._actividad_repository = actividad_repository
        self._usuario_repository = usuario_repository
        self._categoria_repository = categoria_repository
        self._april_month = april_month

    def prepare_form(
        self,
        query: ActividadEditQuery,
        *,
        form_data: ActividadCreateFormData | None = None,
        field_errors: dict[str, str] | None = None,
        general_error: str | None = None,
    ) -> ActividadCreateViewData:
        actor = self._get_active_actor(query.actor_user_id)
        actividad = self._get_editable_activity(
            actividad_id=query.actividad_id,
            actor_user_id=actor.id_usuario,
            actor_role_id=query.actor_role_id,
        )
        categorias = self._categoria_repository.list_all()
        usuarios = (
            self._usuario_repository.list_active_users()
            if query.actor_is_admin
            else [actor]
        )

        return ActividadCreateViewData(
            form=form_data or self._build_form_data_from_activity(actividad),
            categorias=[
                ActividadCreateOptionData(
                    value=categoria.id_categoria,
                    label=categoria.nombre_categoria,
                )
                for categoria in categorias
            ],
            usuarios=[
                ActividadCreateOptionData(
                    value=usuario.id_usuario,
                    label=f"{usuario.nombre} ({usuario.rut})",
                )
                for usuario in usuarios
            ],
            field_errors=field_errors or {},
            general_error=general_error,
            allow_user_selection=query.actor_is_admin,
        )

    def update(self, command: ActividadEditCommand) -> ActividadUpdateResult:
        actor = self._get_active_actor(command.actor_user_id)
        actividad = self._get_editable_activity(
            actividad_id=command.actividad_id,
            actor_user_id=actor.id_usuario,
            actor_role_id=command.actor_role_id,
        )
        field_errors: dict[str, str] = {}

        titulo = command.titulo.strip()
        if not titulo:
            field_errors["titulo"] = "El titulo es obligatorio."

        fecha_actividad = self._parse_date(command.fecha_actividad, field_errors)
        hora_inicio = self._parse_time(
            command.hora_inicio,
            field_errors,
            field_name="hora_inicio",
        )
        hora_fin = self._parse_time(
            command.hora_fin,
            field_errors,
            field_name="hora_fin",
        )
        if hora_inicio is not None and hora_fin is not None and hora_inicio >= hora_fin:
            field_errors["hora_fin"] = "La hora de fin debe ser posterior a la de inicio."

        categoria = self._resolve_categoria(command.id_categoria, field_errors)
        assigned_user = self._resolve_assigned_user(command, actor, field_errors)

        if field_errors:
            raise ActivityEditionValidationError(field_errors=field_errors)

        updated_activity = self._actividad_repository.update(
            actividad,
            titulo=titulo,
            descripcion=self._normalize_optional_text(command.descripcion),
            fecha_actividad=fecha_actividad,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            emoji=self._normalize_optional_text(command.emoji),
            realizada=command.realizada,
            lugar=self._normalize_optional_text(command.lugar),
            id_usuario=assigned_user.id_usuario,
            id_categoria=categoria.id_categoria,
        )
        return ActividadUpdateResult(
            id_actividad=updated_activity.id_actividad,
            titulo=updated_activity.titulo,
        )

    def _get_active_actor(self, actor_user_id: int) -> Usuario:
        actor = self._usuario_repository.get_by_id(actor_user_id)
        if actor is None or not actor.activo:
            raise ActivityPermissionDeniedError(
                "No fue posible resolver un usuario activo para editar actividades."
            )
        return actor

    def _get_editable_activity(
        self,
        *,
        actividad_id: int,
        actor_user_id: int,
        actor_role_id: int,
    ) -> Actividad:
        actividad = self._actividad_repository.get_by_id(actividad_id)
        if actividad is None:
            raise ActivityNotFoundError(f"No existe actividad con id {actividad_id}.")

        actor_is_admin = actor_role_id == ADMIN_ROLE_ID
        if not actor_is_admin and actividad.id_usuario != actor_user_id:
            raise ActivityPermissionDeniedError(
                "El usuario no tiene permisos para editar esta actividad."
            )

        return actividad

    def _build_form_data_from_activity(
        self,
        actividad: Actividad,
    ) -> ActividadCreateFormData:
        return ActividadCreateFormData(
            titulo=actividad.titulo,
            descripcion=actividad.descripcion or "",
            fecha_actividad=actividad.fecha_actividad.isoformat(),
            hora_inicio=actividad.hora_inicio.strftime("%H:%M"),
            hora_fin=actividad.hora_fin.strftime("%H:%M"),
            emoji=actividad.emoji or "",
            lugar=actividad.lugar or "",
            id_categoria=str(actividad.id_categoria),
            id_usuario=str(actividad.id_usuario),
            realizada=actividad.realizada,
        )

    def _parse_date(
        self,
        raw_value: str,
        field_errors: dict[str, str],
    ) -> date | None:
        cleaned_value = raw_value.strip()
        if not cleaned_value:
            field_errors["fecha_actividad"] = "La fecha de actividad es obligatoria."
            return None

        try:
            parsed_date = date.fromisoformat(cleaned_value)
        except ValueError:
            field_errors["fecha_actividad"] = "La fecha ingresada no tiene un formato valido."
            return None

        if parsed_date.month != self._april_month:
            field_errors["fecha_actividad"] = (
                "Solo se permiten actividades entre el 1 y el 30 de abril."
            )
            return None

        return parsed_date

    @staticmethod
    def _parse_time(
        raw_value: str,
        field_errors: dict[str, str],
        *,
        field_name: str,
    ) -> time | None:
        cleaned_value = raw_value.strip()
        if not cleaned_value:
            field_errors[field_name] = "Este horario es obligatorio."
            return None

        try:
            return time.fromisoformat(cleaned_value)
        except ValueError:
            field_errors[field_name] = "La hora ingresada no tiene un formato valido."
            return None

    def _resolve_categoria(
        self,
        raw_value: str,
        field_errors: dict[str, str],
    ) -> Categoria | None:
        categoria_id = self._parse_int(raw_value)
        if categoria_id is None:
            field_errors["id_categoria"] = "Debes seleccionar una categoria valida."
            return None

        categoria = self._categoria_repository.get_by_id(categoria_id)
        if categoria is None:
            field_errors["id_categoria"] = "La categoria seleccionada no existe."
            return None

        return categoria

    def _resolve_assigned_user(
        self,
        command: ActividadEditCommand,
        actor: Usuario,
        field_errors: dict[str, str],
    ) -> Usuario | None:
        if not command.actor_is_admin:
            requested_user_id = self._parse_int(command.id_usuario)
            if (
                requested_user_id is not None
                and requested_user_id != actor.id_usuario
            ):
                raise ActivityPermissionDeniedError(
                    "Un usuario comun solo puede editar actividades propias."
                )
            return actor

        assigned_user_id = self._parse_int(command.id_usuario)
        if assigned_user_id is None:
            field_errors["id_usuario"] = "Debes seleccionar un usuario valido."
            return None

        assigned_user = self._usuario_repository.get_by_id(assigned_user_id)
        if assigned_user is None or not assigned_user.activo:
            field_errors["id_usuario"] = "El usuario seleccionado no esta disponible."
            return None

        return assigned_user

    @staticmethod
    def _parse_int(raw_value: str) -> int | None:
        cleaned_value = raw_value.strip()
        if not cleaned_value:
            return None
        try:
            return int(cleaned_value)
        except ValueError:
            return None

    @staticmethod
    def _normalize_optional_text(raw_value: str) -> str | None:
        cleaned_value = raw_value.strip()
        return cleaned_value or None


def get_actividad_edit_service(
    db: Session = Depends(get_db),
) -> ActividadEditService:
    """Fabrica del servicio de edicion para las rutas HTML."""

    settings = get_settings()
    return ActividadEditService(
        SqlAlchemyActividadRepository(db),
        SqlAlchemyUsuarioRepository(db),
        SqlAlchemyCategoriaRepository(db),
        april_month=settings.april_month,
    )
