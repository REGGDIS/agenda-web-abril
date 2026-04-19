"""Servicio inicial del flujo de login por RUT."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import Depends, status
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings
from backend.app.db.session import get_db
from backend.modulos.auth.esquemas.login import (
    LoginRutResponse,
    SesionLoginData,
    UsuarioLoginData,
)
from backend.modulos.auth.validadores.rut import RutValidationError, validate_rut_or_raise
from backend.modulos.sesiones.modelos import Sesion
from backend.modulos.sesiones.repositorios import SqlAlchemySesionRepository
from backend.modulos.sesiones.servicios import SesionService
from backend.modulos.usuarios.modelos import Usuario
from backend.modulos.usuarios.repositorios import SqlAlchemyUsuarioRepository


class UsuarioLookupRepository(Protocol):
    """Contrato minimo para buscar usuarios por RUT."""

    def get_by_rut(self, rut: str) -> Usuario | None:
        """Busca un usuario por su RUT normalizado."""


class SesionCreator(Protocol):
    """Contrato minimo para crear sesiones del login."""

    def create_session_for_user(self, id_usuario: int) -> Sesion:
        """Crea una sesion activa para el usuario."""


@dataclass(frozen=True)
class LoginExecutionResult:
    """Resultado del flujo inicial de login."""

    http_status: int
    response: LoginRutResponse
    session_cookie_token: str | None = None


class AuthService:
    """Coordina validacion de RUT y consulta de usuario."""

    def __init__(
        self,
        usuario_repository: UsuarioLookupRepository,
        sesion_service: SesionCreator,
    ) -> None:
        self._usuario_repository = usuario_repository
        self._sesion_service = sesion_service

    def prepare_login(self, rut: str) -> LoginExecutionResult:
        try:
            normalized_rut = validate_rut_or_raise(rut)
        except RutValidationError as exc:
            return LoginExecutionResult(
                http_status=status.HTTP_400_BAD_REQUEST,
                response=LoginRutResponse(
                    success=False,
                    status="validation_error",
                    message=exc.message,
                    rut_ingresado=rut,
                    rut_normalizado=None,
                    usuario_existe=False,
                    usuario=None,
                    sesion=None,
                    siguiente_paso="corregir_rut",
                ),
            )

        usuario = self._usuario_repository.get_by_rut(normalized_rut)
        if usuario is None:
            return LoginExecutionResult(
                http_status=status.HTTP_403_FORBIDDEN,
                response=LoginRutResponse(
                    success=False,
                    status="access_denied",
                    message=(
                        "El RUT es valido, pero el usuario no esta autorizado "
                        "para acceder al sistema."
                    ),
                    rut_ingresado=rut,
                    rut_normalizado=normalized_rut,
                    usuario_existe=False,
                    usuario=None,
                    sesion=None,
                    siguiente_paso="acceso_denegado",
                ),
            )

        if not usuario.activo:
            return LoginExecutionResult(
                http_status=status.HTTP_403_FORBIDDEN,
                response=LoginRutResponse(
                    success=False,
                    status="user_inactive",
                    message="El RUT existe, pero el usuario se encuentra inactivo.",
                    rut_ingresado=rut,
                    rut_normalizado=normalized_rut,
                    usuario_existe=True,
                    usuario=self._build_usuario_data(usuario),
                    sesion=None,
                    siguiente_paso="reactivar_usuario",
                ),
            )

        sesion = self._sesion_service.create_session_for_user(usuario.id_usuario)
        return LoginExecutionResult(
            http_status=status.HTTP_200_OK,
            response=LoginRutResponse(
                success=True,
                status="session_created",
                message=(
                    "El RUT es valido, el usuario esta activo y la sesion fue creada."
                ),
                rut_ingresado=rut,
                rut_normalizado=normalized_rut,
                usuario_existe=True,
                usuario=self._build_usuario_data(usuario),
                sesion=self._build_sesion_data(sesion),
                siguiente_paso="validar_sesion_activa",
            ),
            session_cookie_token=sesion.token_sesion,
        )

    @staticmethod
    def _build_usuario_data(usuario: Usuario) -> UsuarioLoginData:
        return UsuarioLoginData(
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            rut=usuario.rut,
            id_rol=usuario.id_rol,
            tema_preferido=usuario.tema_preferido,
            activo=usuario.activo,
        )

    @staticmethod
    def _build_sesion_data(sesion: Sesion) -> SesionLoginData:
        return SesionLoginData(
            id_sesion=sesion.id_sesion,
            id_usuario=sesion.id_usuario,
            fecha_inicio=sesion.fecha_inicio,
            ultimo_movimiento=sesion.ultimo_movimiento,
            activa=sesion.activa,
        )


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Fabrica del servicio de auth para rutas FastAPI."""

    settings = get_settings()
    usuario_repository = SqlAlchemyUsuarioRepository(db)
    sesion_repository = SqlAlchemySesionRepository(db)
    sesion_service = SesionService(
        sesion_repository,
        session_inactivity_minutes=settings.session_inactivity_minutes,
    )
    return AuthService(usuario_repository, sesion_service)
