"""Acceso a datos para categorias visibles en actividades."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.modulos.categorias.modelos import Categoria


class SqlAlchemyCategoriaRepository:
    """Consulta categorias disponibles para clasificar actividades."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_all(self) -> list[Categoria]:
        statement = select(Categoria).order_by(Categoria.nombre_categoria.asc())
        return list(self._db.scalars(statement).all())

    def get_by_id(self, categoria_id: int) -> Categoria | None:
        statement = select(Categoria).where(Categoria.id_categoria == categoria_id)
        return self._db.scalar(statement)
