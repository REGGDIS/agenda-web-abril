"""Servicio para confirmar y ejecutar la eliminacion de actividades."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.modulos.actividades.modelos import Actividad
from backend.modulos.actividades.repositorios import SqlAlchemyActividadRepository
from backend.modulos.actividades.servicios.calendario_service import ADMIN_ROLE_ID
from backend.modulos.actividades.servicios.checklist_service import (
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
)


class ActividadDeleteRepository(Protocol):
    """Contrato minimo para leer y eliminar una actividad existente."""

    def get_by_id(self, actividad_id: int) -> Actividad | None:
        """Busca una actividad por identificador."""

    def delete(self, actividad: Actividad) -> None:
        """Elimina definitivamente una actividad."""


@dataclass(frozen=True)
class ActividadDeleteQuery:
    """Datos necesarios para preparar la confirmacion de borrado."""

    actividad_id: int
    actor_user_id: int
    actor_role_id: int

    @property
    def actor_is_admin(self) -> bool:
        return self.actor_role_id == ADMIN_ROLE_ID


@dataclass(frozen=True)
class ActividadDeleteCommand:
    """Datos necesarios para ejecutar la eliminacion."""

    actividad_id: int
    actor_user_id: int
    actor_role_id: int

    @property
    def actor_is_admin(self) -> bool:
        return self.actor_role_id == ADMIN_ROLE_ID


@dataclass(frozen=True)
class ActividadDeletePreview:
    """Resumen minimo para la pantalla de confirmacion."""

    id_actividad: int
    titulo: str
    descripcion: str | None
    fecha_actividad_label: str
    horario_label: str
    categoria_nombre: str | None
    usuario_nombre: str | None


class ActividadDeleteService:
    """Resuelve permisos y eliminacion real de actividades."""

    def __init__(self, actividad_repository: ActividadDeleteRepository) -> None:
        self._actividad_repository = actividad_repository

    def get_preview(self, query: ActividadDeleteQuery) -> ActividadDeletePreview:
        actividad = self._get_deletable_activity(query)
        categoria_nombre = None
        if actividad.categoria is not None:
            categoria_nombre = actividad.categoria.nombre_categoria

        usuario_nombre = None
        if actividad.usuario is not None:
            usuario_nombre = actividad.usuario.nombre

        return ActividadDeletePreview(
            id_actividad=actividad.id_actividad,
            titulo=actividad.titulo,
            descripcion=actividad.descripcion,
            fecha_actividad_label=actividad.fecha_actividad.strftime("%d/%m/%Y"),
            horario_label=(
                f"{actividad.hora_inicio.strftime('%H:%M')} - "
                f"{actividad.hora_fin.strftime('%H:%M')}"
            ),
            categoria_nombre=categoria_nombre,
            usuario_nombre=usuario_nombre,
        )

    def delete(self, command: ActividadDeleteCommand) -> None:
        actividad = self._get_deletable_activity(command)
        self._actividad_repository.delete(actividad)

    def _get_deletable_activity(
        self,
        request_data: ActividadDeleteQuery | ActividadDeleteCommand,
    ) -> Actividad:
        actividad = self._actividad_repository.get_by_id(request_data.actividad_id)
        if actividad is None:
            raise ActivityNotFoundError(
                f"No existe actividad con id {request_data.actividad_id}."
            )

        if (
            not request_data.actor_is_admin
            and actividad.id_usuario != request_data.actor_user_id
        ):
            raise ActivityPermissionDeniedError(
                "El usuario no tiene permisos para eliminar esta actividad."
            )

        return actividad


def get_actividad_delete_service(
    db: Session = Depends(get_db),
) -> ActividadDeleteService:
    """Fabrica del servicio de eliminacion para rutas HTML."""

    return ActividadDeleteService(SqlAlchemyActividadRepository(db))
