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
