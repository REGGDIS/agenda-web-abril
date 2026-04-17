"""Pruebas del repositorio de actividades para calendario."""

from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.modulos.actividades.modelos import Actividad
from backend.modulos.actividades.repositorios import SqlAlchemyActividadRepository
from backend.modulos.categorias.modelos import Categoria
from backend.modulos.roles.modelos import Rol
from backend.modulos.usuarios.modelos import Usuario


def test_repository_filters_april_and_current_user_for_regular_user():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        _seed_calendar_entities(db)

        repository = SqlAlchemyActividadRepository(db)
        actividades = repository.list_april_activities_for_calendar(
            user_id=2,
            include_all_users=False,
            april_month=4,
        )

        assert len(actividades) == 1
        assert actividades[0].titulo == "Estudiar algebra"
        assert actividades[0].categoria is not None
        assert actividades[0].categoria.nombre_categoria == "Estudio"


def test_repository_can_prepare_admin_view_for_all_users():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        _seed_calendar_entities(db)

        repository = SqlAlchemyActividadRepository(db)
        actividades = repository.list_april_activities_for_calendar(
            user_id=1,
            include_all_users=True,
            april_month=4,
        )

        assert len(actividades) == 2
        assert [actividad.titulo for actividad in actividades] == [
            "Reunion general",
            "Estudiar algebra",
        ]


def test_repository_get_by_id_returns_activity():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        _seed_calendar_entities(db)

        repository = SqlAlchemyActividadRepository(db)
        actividad = repository.get_by_id(2)

        assert actividad is not None
        assert actividad.titulo == "Estudiar algebra"
        assert actividad.realizada is True


def test_repository_update_realizada_persists_new_value():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        _seed_calendar_entities(db)

        repository = SqlAlchemyActividadRepository(db)
        actividad = repository.get_by_id(1)

        assert actividad is not None
        assert actividad.realizada is False

        actualizada = repository.update_realizada(actividad, realizada=True)

        assert actualizada.realizada is True
        refreshed = repository.get_by_id(1)
        assert refreshed is not None
        assert refreshed.realizada is True


def test_repository_create_persists_new_activity():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        _seed_calendar_entities(db)

        repository = SqlAlchemyActividadRepository(db)
        creada = repository.create(
            titulo="Preparar entrega final",
            descripcion="Organizar la demostracion de la agenda.",
            fecha_actividad=date(2026, 4, 21),
            hora_inicio=time(16, 0),
            hora_fin=time(17, 15),
            emoji="🗂️",
            realizada=False,
            lugar="Laboratorio",
            id_usuario=2,
            id_categoria=1,
            fecha_creacion=datetime(2026, 4, 17, 12, 30, 0),
        )

        assert creada.id_actividad is not None
        assert creada.titulo == "Preparar entrega final"

        persisted = repository.get_by_id(creada.id_actividad)
        assert persisted is not None
        assert persisted.titulo == "Preparar entrega final"
        assert persisted.fecha_actividad == date(2026, 4, 21)
        assert persisted.categoria is not None
        assert persisted.categoria.nombre_categoria == "Trabajo"


def test_repository_update_persists_activity_changes():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        _seed_calendar_entities(db)

        repository = SqlAlchemyActividadRepository(db)
        actividad = repository.get_by_id(2)

        assert actividad is not None

        actualizada = repository.update(
            actividad,
            titulo="Algebra avanzada",
            descripcion="Resolver una nueva guia.",
            fecha_actividad=date(2026, 4, 14),
            hora_inicio=time(19, 0),
            hora_fin=time(20, 0),
            emoji="🧠",
            realizada=False,
            lugar="Biblioteca",
            id_usuario=1,
            id_categoria=1,
        )

        assert actualizada.titulo == "Algebra avanzada"

        persisted = repository.get_by_id(2)
        assert persisted is not None
        assert persisted.titulo == "Algebra avanzada"
        assert persisted.descripcion == "Resolver una nueva guia."
        assert persisted.fecha_actividad == date(2026, 4, 14)
        assert persisted.hora_inicio == time(19, 0)
        assert persisted.hora_fin == time(20, 0)
        assert persisted.realizada is False
        assert persisted.lugar == "Biblioteca"
        assert persisted.id_usuario == 1
        assert persisted.id_categoria == 1


def test_repository_delete_removes_activity_from_database():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        _seed_calendar_entities(db)

        repository = SqlAlchemyActividadRepository(db)
        actividad = repository.get_by_id(2)

        assert actividad is not None

        repository.delete(actividad)

        assert repository.get_by_id(2) is None
        actividades = repository.list_april_activities_for_calendar(
            user_id=1,
            include_all_users=True,
            april_month=4,
        )
        assert [item.id_actividad for item in actividades] == [1]


def _seed_calendar_entities(db: Session) -> None:
    db.add_all(
        [
            Rol(id_rol=1, nombre_rol="administrador", descripcion="Administrador"),
            Rol(id_rol=2, nombre_rol="usuario", descripcion="Usuario comun"),
            Usuario(
                id_usuario=1,
                nombre="Administrador",
                rut="12.345.678-5",
                id_rol=1,
                tema_preferido="light",
                activo=True,
                fecha_creacion=datetime(2026, 4, 1, 8, 0, 0),
            ),
            Usuario(
                id_usuario=2,
                nombre="Usuario Abril",
                rut="11.111.111-1",
                id_rol=2,
                tema_preferido="dark",
                activo=True,
                fecha_creacion=datetime(2026, 4, 1, 8, 30, 0),
            ),
            Categoria(
                id_categoria=1,
                nombre_categoria="Trabajo",
                descripcion="Tareas laborales",
            ),
            Categoria(
                id_categoria=2,
                nombre_categoria="Estudio",
                descripcion="Actividades de estudio",
            ),
            Actividad(
                id_actividad=1,
                titulo="Reunion general",
                descripcion="Revision semanal del proyecto.",
                fecha_actividad=date(2026, 4, 10),
                hora_inicio=time(9, 0),
                hora_fin=time(10, 0),
                emoji="📌",
                realizada=False,
                lugar="Sala 1",
                id_usuario=1,
                id_categoria=1,
                fecha_creacion=datetime(2026, 4, 5, 10, 0, 0),
            ),
            Actividad(
                id_actividad=2,
                titulo="Estudiar algebra",
                descripcion="Resolver ejercicios clave.",
                fecha_actividad=date(2026, 4, 12),
                hora_inicio=time(18, 0),
                hora_fin=time(19, 30),
                emoji="📚",
                realizada=True,
                lugar="Casa",
                id_usuario=2,
                id_categoria=2,
                fecha_creacion=datetime(2026, 4, 5, 11, 0, 0),
            ),
            Actividad(
                id_actividad=3,
                titulo="Actividad fuera de abril",
                descripcion="No debe aparecer.",
                fecha_actividad=date(2026, 5, 3),
                hora_inicio=time(10, 0),
                hora_fin=time(11, 0),
                emoji=None,
                realizada=False,
                lugar="Oficina",
                id_usuario=2,
                id_categoria=1,
                fecha_creacion=datetime(2026, 4, 5, 12, 0, 0),
            ),
        ]
    )
    db.commit()
