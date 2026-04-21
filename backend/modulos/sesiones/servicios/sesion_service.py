"""Servicio de creacion y consulta basica de sesiones."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from fastapi import Depends, status
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings
from backend.app.db.session import get_db
from backend.modulos.sesiones.esquemas import (
    SesionActualData,
    SesionActualResponse,
    SesionActualUsuarioData,
)
from backend.modulos.sesiones.modelos import Sesion
from backend.modulos.sesiones.repositorios import SqlAlchemySesionRepository


class SesionRepository(Protocol):
    """Contrato minimo para persistencia de sesiones."""

    def create(
        self,
        *,
        id_usuario: int,
        token_sesion: str,
        fecha_inicio: datetime,
        ultimo_movimiento: datetime,
    ) -> Sesion:
        """Crea una sesion persistida."""

    def get_active_by_token(self, token_sesion: str) -> Sesion | None:
        """Busca una sesion activa por token."""

    def get_by_token(self, token_sesion: str) -> Sesion | None:
        """Busca una sesion por token sin filtrar por estado."""

    def touch_last_movement(
        self,
        sesion: Sesion,
        *,
        ultimo_movimiento: datetime,
    ) -> Sesion:
        """Actualiza el ultimo movimiento de una sesion."""

    def close_session(
        self,
        sesion: Sesion,
        *,
        fecha_cierre: datetime,
    ) -> Sesion:
        """Cierra una sesion activa y registra su fecha de cierre."""


@dataclass(frozen=True)
class SesionResolutionResult:
    """Resultado de resolver la sesion actual desde un token."""

    http_status: int
    response: SesionActualResponse


class SesionService:
    """Orquesta la creacion y lectura inicial de sesiones."""

    def __init__(
        self,
        sesion_repository: SesionRepository,
        *,
        session_inactivity_minutes: int,
    ) -> None:
        self._sesion_repository = sesion_repository
        self._session_inactivity_delta = timedelta(
            minutes=session_inactivity_minutes
        )

    def create_session_for_user(self, id_usuario: int) -> Sesion:
        now = datetime.now()
        token_sesion = secrets.token_urlsafe(32)
        return self._sesion_repository.create(
            id_usuario=id_usuario,
            token_sesion=token_sesion,
            fecha_inicio=now,
            ultimo_movimiento=now,
        )

    def get_active_session_by_token(self, token_sesion: str) -> Sesion | None:
        return self._sesion_repository.get_active_by_token(token_sesion)

    def resolve_session_from_token(self, token_sesion: str | None) -> SesionResolutionResult:
        return self._resolve_token_operation(
            token_sesion,
            should_touch_last_movement=False,
        )

    def register_activity_from_token(
        self,
        token_sesion: str | None,
    ) -> SesionResolutionResult:
        return self._resolve_token_operation(
            token_sesion,
            should_touch_last_movement=True,
        )

    def expire_session_from_token(self, token_sesion: str | None) -> SesionResolutionResult:
        if token_sesion is None or not token_sesion.strip():
            return self._build_cookie_missing_result()

        sesion = self._sesion_repository.get_by_token(token_sesion)
        if sesion is None:
            return self._build_session_not_found_result()

        if not sesion.activa:
            return self._build_inactive_result(sesion)

        closed_session = self._sesion_repository.close_session(
            sesion,
            fecha_cierre=datetime.now(),
        )
        return SesionResolutionResult(
            http_status=status.HTTP_401_UNAUTHORIZED,
            response=SesionActualResponse(
                success=False,
                status="session_expired",
                message="La sesion fue cerrada por inactividad.",
                cookie_present=True,
                session_found=True,
                session_active=False,
                ultimo_movimiento_actualizado=False,
                ultimo_movimiento_anterior=sesion.ultimo_movimiento,
                sesion=self._build_session_data(closed_session),
                usuario=self._build_user_data(closed_session),
            ),
        )

    def close_session_from_token(self, token_sesion: str | None) -> SesionResolutionResult:
        if token_sesion is None or not token_sesion.strip():
            return self._build_cookie_missing_result()

        sesion = self._sesion_repository.get_by_token(token_sesion)
        if sesion is None:
            return self._build_session_not_found_result()

        if not sesion.activa:
            return self._build_inactive_result(sesion)

        closed_session = self._sesion_repository.close_session(
            sesion,
            fecha_cierre=datetime.now(),
        )
        return SesionResolutionResult(
            http_status=status.HTTP_200_OK,
            response=SesionActualResponse(
                success=True,
                status="session_closed",
                message="La sesion fue cerrada correctamente.",
                cookie_present=True,
                session_found=True,
                session_active=False,
                ultimo_movimiento_actualizado=False,
                ultimo_movimiento_anterior=sesion.ultimo_movimiento,
                sesion=self._build_session_data(closed_session),
                usuario=self._build_user_data(closed_session),
            ),
        )

    def _resolve_token_operation(
        self,
        token_sesion: str | None,
        *,
        should_touch_last_movement: bool,
    ) -> SesionResolutionResult:
        if token_sesion is None or not token_sesion.strip():
            return self._build_cookie_missing_result()

        sesion = self._sesion_repository.get_by_token(token_sesion)
        if sesion is None:
            return self._build_session_not_found_result()

        if not sesion.activa:
            return self._build_inactive_result(sesion)

        now = datetime.now()
        if self._session_has_expired(sesion, now):
            closed_session = self._sesion_repository.close_session(
                sesion,
                fecha_cierre=now,
            )
            return SesionResolutionResult(
                http_status=status.HTTP_401_UNAUTHORIZED,
                response=SesionActualResponse(
                    success=False,
                    status="session_expired",
                    message="La sesion expiro por inactividad.",
                    cookie_present=True,
                    session_found=True,
                    session_active=False,
                    ultimo_movimiento_actualizado=False,
                    ultimo_movimiento_anterior=sesion.ultimo_movimiento,
                    sesion=self._build_session_data(closed_session),
                    usuario=self._build_user_data(closed_session),
                ),
            )

        resolved_session = sesion
        previous_last_movement = None
        movement_updated = False
        message = "La cookie es valida y la sesion sigue activa."
        if should_touch_last_movement:
            previous_last_movement = sesion.ultimo_movimiento
            resolved_session = self._sesion_repository.touch_last_movement(
                sesion,
                ultimo_movimiento=now,
            )
            movement_updated = True
            message = "La actividad del usuario fue registrada en la sesion activa."

        return SesionResolutionResult(
            http_status=status.HTTP_200_OK,
            response=SesionActualResponse(
                success=True,
                status="session_valid",
                message=message,
                cookie_present=True,
                session_found=True,
                session_active=True,
                ultimo_movimiento_actualizado=movement_updated,
                ultimo_movimiento_anterior=previous_last_movement,
                sesion=self._build_session_data(resolved_session),
                usuario=self._build_user_data(resolved_session),
            ),
        )

    def _build_cookie_missing_result(self) -> SesionResolutionResult:
        return SesionResolutionResult(
            http_status=status.HTTP_401_UNAUTHORIZED,
            response=SesionActualResponse(
                success=False,
                status="cookie_missing",
                message="No existe cookie de sesion en la solicitud.",
                cookie_present=False,
                session_found=False,
                session_active=False,
                ultimo_movimiento_actualizado=False,
                ultimo_movimiento_anterior=None,
                sesion=None,
                usuario=None,
            ),
        )

    def _build_session_not_found_result(self) -> SesionResolutionResult:
        return SesionResolutionResult(
            http_status=status.HTTP_401_UNAUTHORIZED,
            response=SesionActualResponse(
                success=False,
                status="session_not_found",
                message="La cookie existe, pero no corresponde a una sesion registrada.",
                cookie_present=True,
                session_found=False,
                session_active=False,
                ultimo_movimiento_actualizado=False,
                ultimo_movimiento_anterior=None,
                sesion=None,
                usuario=None,
            ),
        )

    def _build_inactive_result(self, sesion: Sesion) -> SesionResolutionResult:
        return SesionResolutionResult(
            http_status=status.HTTP_403_FORBIDDEN,
            response=SesionActualResponse(
                success=False,
                status="session_inactive",
                message="La sesion existe, pero se encuentra inactiva.",
                cookie_present=True,
                session_found=True,
                session_active=False,
                ultimo_movimiento_actualizado=False,
                ultimo_movimiento_anterior=sesion.ultimo_movimiento,
                sesion=self._build_session_data(sesion),
                usuario=self._build_user_data(sesion),
            ),
        )

    def _session_has_expired(self, sesion: Sesion, reference_time: datetime) -> bool:
        return (
            reference_time - sesion.ultimo_movimiento
        ) >= self._session_inactivity_delta

    @staticmethod
    def _build_session_data(sesion: Sesion) -> SesionActualData:
        return SesionActualData(
            id_sesion=sesion.id_sesion,
            id_usuario=sesion.id_usuario,
            fecha_inicio=sesion.fecha_inicio,
            ultimo_movimiento=sesion.ultimo_movimiento,
            fecha_cierre=sesion.fecha_cierre,
            activa=sesion.activa,
        )

    @staticmethod
    def _build_user_data(sesion: Sesion) -> SesionActualUsuarioData | None:
        if sesion.usuario is None:
            return None
        return SesionActualUsuarioData(
            id_usuario=sesion.usuario.id_usuario,
            nombre=sesion.usuario.nombre,
            rut=sesion.usuario.rut,
            id_rol=sesion.usuario.id_rol,
            tema_preferido=sesion.usuario.tema_preferido,
            activo=sesion.usuario.activo,
        )


def get_sesion_service(db: Session = Depends(get_db)) -> SesionService:
    """Fabrica del servicio de sesiones para rutas o dependencias."""

    settings = get_settings()
    sesion_repository = SqlAlchemySesionRepository(db)
    return SesionService(
        sesion_repository,
        session_inactivity_minutes=settings.session_inactivity_minutes,
    )
