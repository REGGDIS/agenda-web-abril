"""Acceso a datos minimo para sesiones."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from backend.modulos.sesiones.modelos import Sesion


class SqlAlchemySesionRepository:
    """Persistencia de sesiones para el login inicial."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _get_by_token_statement(self, token_sesion: str):
        return (
            select(Sesion)
            .options(selectinload(Sesion.usuario))
            .where(Sesion.token_sesion == token_sesion)
        )

    def create(
        self,
        *,
        id_usuario: int,
        token_sesion: str,
        fecha_inicio: datetime,
        ultimo_movimiento: datetime,
    ) -> Sesion:
        sesion = Sesion(
            id_usuario=id_usuario,
            token_sesion=token_sesion,
            fecha_inicio=fecha_inicio,
            ultimo_movimiento=ultimo_movimiento,
            fecha_cierre=None,
            activa=True,
        )
        self._db.add(sesion)
        self._db.commit()
        self._db.refresh(sesion)
        return sesion

    def get_by_token(self, token_sesion: str) -> Sesion | None:
        statement = self._get_by_token_statement(token_sesion)
        return self._db.scalar(statement)

    def get_active_by_token(self, token_sesion: str) -> Sesion | None:
        statement = self._get_by_token_statement(token_sesion).where(
            Sesion.activa.is_(True),
        )
        return self._db.scalar(statement)

    def touch_last_movement(
        self,
        sesion: Sesion,
        *,
        ultimo_movimiento: datetime,
    ) -> Sesion:
        sesion.ultimo_movimiento = ultimo_movimiento
        self._db.add(sesion)
        self._db.commit()
        refreshed_session = self._db.scalar(
            self._get_by_token_statement(sesion.token_sesion)
        )
        if refreshed_session is None:
            raise LookupError("La sesion actualizada no pudo recargarse desde la base.")
        return refreshed_session

    def close_session(
        self,
        sesion: Sesion,
        *,
        fecha_cierre: datetime,
    ) -> Sesion:
        sesion.fecha_cierre = fecha_cierre
        sesion.activa = False
        self._db.add(sesion)
        self._db.commit()
        refreshed_session = self._db.scalar(
            self._get_by_token_statement(sesion.token_sesion)
        )
        if refreshed_session is None:
            raise LookupError("La sesion cerrada no pudo recargarse desde la base.")
        return refreshed_session
