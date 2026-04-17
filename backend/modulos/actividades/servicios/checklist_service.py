"""Servicio minimo para checklist real de actividades."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.modulos.actividades.modelos import Actividad
from backend.modulos.actividades.repositorios import SqlAlchemyActividadRepository
from backend.modulos.actividades.servicios.calendario_service import ADMIN_ROLE_ID


class ActivityChecklistError(Exception):
    """Base para errores controlados del checklist."""


class ActivityNotFoundError(ActivityChecklistError):
    """Se lanza cuando la actividad no existe."""


class ActivityPermissionDeniedError(ActivityChecklistError):
    """Se lanza cuando el usuario no puede modificar la actividad."""


class ActividadChecklistRepository(Protocol):
    """Contrato minimo para buscar y actualizar actividades."""

    def get_by_id(self, actividad_id: int) -> Actividad | None:
        """Busca una actividad por su identificador."""

    def update_realizada(
        self,
        actividad: Actividad,
        *,
        realizada: bool,
    ) -> Actividad:
        """Persista el nuevo estado de checklist."""


@dataclass(frozen=True)
class ActividadChecklistCommand:
    """Datos necesarios para cambiar el estado de una actividad."""

    actividad_id: int
    actor_user_id: int
    actor_role_id: int
    realizada: bool

    @property
    def actor_is_admin(self) -> bool:
        return self.actor_role_id == ADMIN_ROLE_ID


class ActividadChecklistService:
    """Orquesta el cambio de estado realizada/no realizada."""

    def __init__(self, actividad_repository: ActividadChecklistRepository) -> None:
        self._actividad_repository = actividad_repository

    def set_realizada(self, command: ActividadChecklistCommand) -> Actividad:
        actividad = self._actividad_repository.get_by_id(command.actividad_id)
        if actividad is None:
            raise ActivityNotFoundError(
                f"No existe actividad con id {command.actividad_id}."
            )

        if not command.actor_is_admin and actividad.id_usuario != command.actor_user_id:
            raise ActivityPermissionDeniedError(
                "El usuario no tiene permisos para modificar esta actividad."
            )

        if actividad.realizada == command.realizada:
            return actividad

        return self._actividad_repository.update_realizada(
            actividad,
            realizada=command.realizada,
        )


def get_actividad_checklist_service(
    db: Session = Depends(get_db),
) -> ActividadChecklistService:
    """Fabrica del servicio de checklist para la vista del calendario."""

    actividad_repository = SqlAlchemyActividadRepository(db)
    return ActividadChecklistService(actividad_repository)
