"""Acceso a datos para lectura y cambio de estado de actividades."""

from __future__ import annotations

from datetime import date

from sqlalchemy import extract, select
from sqlalchemy.orm import Session, selectinload

from backend.modulos.actividades.modelos import Actividad


class SqlAlchemyActividadRepository:
    """Consulta y actualiza actividades reales del calendario."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_april_activities_for_calendar(
        self,
        *,
        user_id: int,
        include_all_users: bool,
        april_month: int,
    ) -> list[Actividad]:
        statement = (
            select(Actividad)
            .options(selectinload(Actividad.categoria), selectinload(Actividad.usuario))
            .where(extract("month", Actividad.fecha_actividad) == april_month)
            .order_by(Actividad.fecha_actividad.asc(), Actividad.hora_inicio.asc())
        )

        if not include_all_users:
            statement = statement.where(Actividad.id_usuario == user_id)

        return list(self._db.scalars(statement).all())

    def get_by_id(self, actividad_id: int) -> Actividad | None:
        statement = (
            select(Actividad)
            .options(selectinload(Actividad.categoria), selectinload(Actividad.usuario))
            .where(Actividad.id_actividad == actividad_id)
        )
        return self._db.scalar(statement)

    def update_realizada(
        self,
        actividad: Actividad,
        *,
        realizada: bool,
    ) -> Actividad:
        actividad.realizada = realizada
        self._db.add(actividad)
        self._db.commit()
        self._db.refresh(actividad)
        return actividad
