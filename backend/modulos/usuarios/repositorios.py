"""Acceso a datos minimo para usuarios."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.modulos.usuarios.modelos import Usuario


class SqlAlchemyUsuarioRepository:
    """Consulta usuarios sin acoplar el servicio de auth al ORM."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_rut(self, rut: str) -> Usuario | None:
        normalized_input = rut.replace("-", "")
        normalized_column = func.upper(
            func.replace(
                func.replace(
                    func.replace(Usuario.rut, ".", ""),
                    "-",
                    "",
                ),
                " ",
                "",
            )
        )
        statement = select(Usuario).where(normalized_column == normalized_input)
        return self._db.scalar(statement)

    def get_by_id(self, user_id: int) -> Usuario | None:
        statement = select(Usuario).where(Usuario.id_usuario == user_id)
        return self._db.scalar(statement)

    def list_active_users(self) -> list[Usuario]:
        statement = (
            select(Usuario)
            .where(Usuario.activo.is_(True))
            .order_by(Usuario.nombre.asc(), Usuario.id_usuario.asc())
        )
        return list(self._db.scalars(statement).all())
