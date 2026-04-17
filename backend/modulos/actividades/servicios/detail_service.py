"""Servicio para consultar el detalle visible de una actividad."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.modulos.actividades.esquemas import ActividadDetalleData
from backend.modulos.actividades.modelos import Actividad
from backend.modulos.actividades.repositorios import SqlAlchemyActividadRepository
from backend.modulos.actividades.servicios.calendario_service import ADMIN_ROLE_ID
from backend.modulos.actividades.servicios.checklist_service import (
    ActivityNotFoundError,
    ActivityPermissionDeniedError,
)


class ActividadDetailRepository(Protocol):
    """Contrato minimo para buscar actividades con sus relaciones."""

    def get_by_id(self, actividad_id: int) -> Actividad | None:
        """Retorna una actividad o None."""


@dataclass(frozen=True)
class ActividadDetailQuery:
    """Datos del actor actual y de la actividad solicitada."""

    actividad_id: int
    actor_user_id: int
    actor_role_id: int

    @property
    def actor_is_admin(self) -> bool:
        return self.actor_role_id == ADMIN_ROLE_ID


class ActividadDetailService:
    """Resuelve el detalle de actividad respetando permisos del proyecto."""

    def __init__(self, actividad_repository: ActividadDetailRepository) -> None:
        self._actividad_repository = actividad_repository

    def get_detail(self, query: ActividadDetailQuery) -> ActividadDetalleData:
        actividad = self._actividad_repository.get_by_id(query.actividad_id)
        if actividad is None:
            raise ActivityNotFoundError(
                f"No existe actividad con id {query.actividad_id}."
            )

        if not query.actor_is_admin and actividad.id_usuario != query.actor_user_id:
            raise ActivityPermissionDeniedError(
                "El usuario no tiene permisos para ver esta actividad."
            )

        categoria_nombre = None
        categoria_descripcion = None
        if actividad.categoria is not None:
            categoria_nombre = actividad.categoria.nombre_categoria
            categoria_descripcion = actividad.categoria.descripcion

        usuario_nombre = None
        usuario_rut = None
        if actividad.usuario is not None:
            usuario_nombre = actividad.usuario.nombre
            usuario_rut = actividad.usuario.rut

        return ActividadDetalleData(
            id_actividad=actividad.id_actividad,
            titulo=actividad.titulo,
            descripcion=actividad.descripcion,
            fecha_actividad=actividad.fecha_actividad,
            hora_inicio=actividad.hora_inicio,
            hora_fin=actividad.hora_fin,
            emoji=actividad.emoji,
            realizada=actividad.realizada,
            lugar=actividad.lugar,
            categoria_nombre=categoria_nombre,
            categoria_descripcion=categoria_descripcion,
            id_usuario=actividad.id_usuario,
            usuario_nombre=usuario_nombre,
            usuario_rut=usuario_rut,
            fecha_creacion=actividad.fecha_creacion,
        )


def get_actividad_detail_service(
    db: Session = Depends(get_db),
) -> ActividadDetailService:
    """Fabrica del servicio de detalle de actividad."""

    actividad_repository = SqlAlchemyActividadRepository(db)
    return ActividadDetailService(actividad_repository)
