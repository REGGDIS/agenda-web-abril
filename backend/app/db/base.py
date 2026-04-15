"""Registro central de modelos ORM para SQLAlchemy y Alembic."""

from backend.app.db.base_class import Base


from backend.modulos.roles.modelos import Rol  # noqa: E402,F401
from backend.modulos.sesiones.modelos import Sesion  # noqa: E402,F401
from backend.modulos.usuarios.modelos import Usuario  # noqa: E402,F401
