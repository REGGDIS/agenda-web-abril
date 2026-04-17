"""Servicio para preparar y persistir la creacion de actividades."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Protocol

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings
from backend.app.db.session import get_db
from backend.modulos.actividades.esquemas import (
    ActividadCreateFormData,
    ActividadCreateOptionData,
    ActividadCreateResult,
    ActividadCreateViewData,
)
from backend.modulos.actividades.modelos import Actividad
from backend.modulos.actividades.repositorios import SqlAlchemyActividadRepository
from backend.modulos.actividades.servicios.calendario_service import ADMIN_ROLE_ID
from backend.modulos.categorias.modelos import Categoria
from backend.modulos.categorias.repositorios import SqlAlchemyCategoriaRepository
from backend.modulos.usuarios.modelos import Usuario
from backend.modulos.usuarios.repositorios import SqlAlchemyUsuarioRepository


class ActivityCreationError(Exception):
    """Base para errores controlados del flujo de creacion."""


class ActivityCreationPermissionDeniedError(ActivityCreationError):
    """Se lanza cuando el usuario no puede crear para el destino solicitado."""


class ActivityCreationValidationError(ActivityCreationError):
    """Se lanza cuando los datos del formulario no son validos."""

    def __init__(
        self,
        *,
        field_errors: dict[str, str],
        general_error: str = "Revisa los datos obligatorios del formulario.",
    ) -> None:
        super().__init__(general_error)
        self.field_errors = field_errors
        self.general_error = general_error


class ActividadCreateRepository(Protocol):
    """Contrato minimo para persistir una actividad nueva."""

    def create(
        self,
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
        fecha_creacion: datetime,
    ) -> Actividad:
        """Crea y persiste una actividad."""


class UsuarioCreateRepository(Protocol):
    """Contrato minimo para resolver usuarios asignables."""

    def get_by_id(self, user_id: int) -> Usuario | None:
        """Busca un usuario por identificador."""

    def list_active_users(self) -> list[Usuario]:
        """Obtiene los usuarios activos visibles para asignacion."""


class CategoriaCreateRepository(Protocol):
    """Contrato minimo para resolver categorias disponibles."""

    def get_by_id(self, categoria_id: int) -> Categoria | None:
        """Busca una categoria por identificador."""

    def list_all(self) -> list[Categoria]:
        """Obtiene todas las categorias registradas."""


@dataclass(frozen=True)
class ActividadCreateFormQuery:
    """Datos del actor necesarios para preparar la vista del formulario."""

    actor_user_id: int
    actor_role_id: int

    @property
    def actor_is_admin(self) -> bool:
        return self.actor_role_id == ADMIN_ROLE_ID


@dataclass(frozen=True)
class ActividadCreateCommand:
    """Datos crudos recibidos desde el formulario HTML."""

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


class ActividadCreateService:
    """Coordina permisos, validaciones y persistencia de una actividad."""

    def __init__(
        self,
        actividad_repository: ActividadCreateRepository,
        usuario_repository: UsuarioCreateRepository,
        categoria_repository: CategoriaCreateRepository,
        *,
        april_month: int,
    ) -> None:
        self._actividad_repository = actividad_repository
        self._usuario_repository = usuario_repository
        self._categoria_repository = categoria_repository
        self._april_month = april_month

    def prepare_form(
        self,
        query: ActividadCreateFormQuery,
        *,
        form_data: ActividadCreateFormData | None = None,
        field_errors: dict[str, str] | None = None,
        general_error: str | None = None,
    ) -> ActividadCreateViewData:
        actor = self._get_active_actor(query.actor_user_id)
        categorias = self._categoria_repository.list_all()
        usuarios = (
            self._usuario_repository.list_active_users()
            if query.actor_is_admin
            else [actor]
        )

        default_form = form_data or ActividadCreateFormData()
        if not default_form.id_usuario:
            default_form = default_form.model_copy(
                update={"id_usuario": str(actor.id_usuario)}
            )

        return ActividadCreateViewData(
            form=default_form,
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

    def create(self, command: ActividadCreateCommand) -> ActividadCreateResult:
        actor = self._get_active_actor(command.actor_user_id)
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
            raise ActivityCreationValidationError(field_errors=field_errors)

        actividad = self._actividad_repository.create(
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
            fecha_creacion=datetime.now(),
        )
        return ActividadCreateResult(
            id_actividad=actividad.id_actividad,
            titulo=actividad.titulo,
        )

    def _get_active_actor(self, actor_user_id: int) -> Usuario:
        actor = self._usuario_repository.get_by_id(actor_user_id)
        if actor is None or not actor.activo:
            raise ActivityCreationPermissionDeniedError(
                "No fue posible resolver un usuario activo para crear actividades."
            )
        return actor

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
        command: ActividadCreateCommand,
        actor: Usuario,
        field_errors: dict[str, str],
    ) -> Usuario | None:
        if not command.actor_is_admin:
            requested_user_id = self._parse_int(command.id_usuario)
            if (
                requested_user_id is not None
                and requested_user_id != actor.id_usuario
            ):
                raise ActivityCreationPermissionDeniedError(
                    "Un usuario comun solo puede crear actividades para si mismo."
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


def get_actividad_create_service(
    db: Session = Depends(get_db),
) -> ActividadCreateService:
    """Fabrica del servicio de creacion para las rutas HTML."""

    settings = get_settings()
    return ActividadCreateService(
        SqlAlchemyActividadRepository(db),
        SqlAlchemyUsuarioRepository(db),
        SqlAlchemyCategoriaRepository(db),
        april_month=settings.april_month,
    )
