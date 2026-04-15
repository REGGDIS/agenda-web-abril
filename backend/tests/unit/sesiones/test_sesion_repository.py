"""Pruebas del repositorio SQLAlchemy de sesiones."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.modulos.roles.modelos import Rol
from backend.modulos.sesiones.repositorios import SqlAlchemySesionRepository
from backend.modulos.usuarios.modelos import Usuario


def test_sesion_repository_creates_and_queries_active_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        rol = Rol(id_rol=1, nombre_rol="administrador", descripcion="Administrador")
        usuario = Usuario(
            id_usuario=1,
            nombre="Administrador",
            rut="12.345.678-5",
            id_rol=1,
            tema_preferido="light",
            activo=True,
            fecha_creacion=datetime(2026, 4, 15, 9, 0, 0),
        )
        db.add(rol)
        db.add(usuario)
        db.commit()

        repository = SqlAlchemySesionRepository(db)
        created = repository.create(
            id_usuario=1,
            token_sesion="token-prueba",
            fecha_inicio=datetime(2026, 4, 15, 10, 0, 0),
            ultimo_movimiento=datetime(2026, 4, 15, 10, 0, 0),
        )

        found = repository.get_active_by_token("token-prueba")

        assert created.id_sesion is not None
        assert found is not None
        assert found.id_usuario == 1
        assert found.activa is True
        assert found.usuario is not None
        assert found.usuario.nombre == "Administrador"


def test_sesion_repository_updates_last_movement():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        rol = Rol(id_rol=1, nombre_rol="administrador", descripcion="Administrador")
        usuario = Usuario(
            id_usuario=1,
            nombre="Administrador",
            rut="12.345.678-5",
            id_rol=1,
            tema_preferido="light",
            activo=True,
            fecha_creacion=datetime(2026, 4, 15, 9, 0, 0),
        )
        db.add(rol)
        db.add(usuario)
        db.commit()

        repository = SqlAlchemySesionRepository(db)
        created = repository.create(
            id_usuario=1,
            token_sesion="token-touch",
            fecha_inicio=datetime(2026, 4, 15, 10, 0, 0),
            ultimo_movimiento=datetime(2026, 4, 15, 10, 0, 0),
        )

        updated = repository.touch_last_movement(
            created,
            ultimo_movimiento=datetime(2026, 4, 15, 10, 1, 0),
        )

        assert updated.ultimo_movimiento == datetime(2026, 4, 15, 10, 1, 0)
        assert updated.usuario is not None
        assert updated.usuario.id_usuario == 1
