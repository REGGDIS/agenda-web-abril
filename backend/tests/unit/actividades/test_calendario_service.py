"""Pruebas del servicio de calendario basado en actividades."""

from __future__ import annotations

from datetime import date, time

from backend.modulos.actividades.servicios import (
    ActividadCalendarQuery,
    ActividadCalendarService,
)


class StubActividadRepository:
    def __init__(self) -> None:
        self.last_query: dict[str, object] | None = None
        self.return_all_done_today = False

    def list_april_activities_for_calendar(
        self,
        *,
        user_id: int,
        include_all_users: bool,
        april_month: int,
    ):
        self.last_query = {
            "user_id": user_id,
            "include_all_users": include_all_users,
            "april_month": april_month,
        }
        first_today_done = self.return_all_done_today
        return [
            _FakeActividad(
                id_actividad=10,
                titulo="Actividad A",
                fecha_actividad=date(2026, 4, 10),
                hora_inicio=time(9, 0),
                hora_fin=time(10, 0),
                descripcion="Primera actividad",
                emoji="📌",
                realizada=first_today_done,
                lugar="Sala 1",
                id_usuario=2,
                categoria=_FakeCategoria("Trabajo"),
            ),
            _FakeActividad(
                id_actividad=11,
                titulo="Actividad B",
                fecha_actividad=date(2026, 4, 10),
                hora_inicio=time(11, 0),
                hora_fin=time(12, 0),
                descripcion=None,
                emoji=None,
                realizada=True,
                lugar=None,
                id_usuario=2,
                categoria=_FakeCategoria("Estudio"),
            ),
            _FakeActividad(
                id_actividad=12,
                titulo="Actividad C",
                fecha_actividad=date(2026, 4, 12),
                hora_inicio=time(14, 0),
                hora_fin=time(15, 0),
                descripcion="Tercera actividad",
                emoji="✅",
                realizada=True,
                lugar="Casa",
                id_usuario=2,
                categoria=_FakeCategoria("Personal"),
            ),
        ]


class _FakeCategoria:
    def __init__(self, nombre_categoria: str) -> None:
        self.nombre_categoria = nombre_categoria


class _FakeActividad:
    def __init__(
        self,
        *,
        id_actividad: int,
        titulo: str,
        fecha_actividad: date,
        hora_inicio: time,
        hora_fin: time,
        descripcion: str | None,
        emoji: str | None,
        realizada: bool,
        lugar: str | None,
        id_usuario: int,
        categoria: _FakeCategoria | None,
    ) -> None:
        self.id_actividad = id_actividad
        self.titulo = titulo
        self.fecha_actividad = fecha_actividad
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.descripcion = descripcion
        self.emoji = emoji
        self.realizada = realizada
        self.lugar = lugar
        self.id_usuario = id_usuario
        self.categoria = categoria


def test_calendar_service_groups_activities_by_day():
    repository = StubActividadRepository()
    service = ActividadCalendarService(
        repository,
        april_month=4,
        today_provider=lambda: date(2026, 4, 10),
    )

    result = service.get_calendar_data(ActividadCalendarQuery(user_id=2, role_id=2))

    assert repository.last_query == {
        "user_id": 2,
        "include_all_users": False,
        "april_month": 4,
    }
    assert result.total_actividades == 3
    assert result.total_dias_con_actividades == 2
    assert result.month_label == "Abril 2026"
    assert result.weekday_labels == [
        "Lunes",
        "Martes",
        "Miercoles",
        "Jueves",
        "Viernes",
        "Sabado",
        "Domingo",
    ]
    assert result.day_blocks[0].etiqueta_dia == "10/04/2026"
    assert result.day_blocks[0].total_actividades == 2
    assert result.day_blocks[1].actividades[0].categoria_nombre == "Personal"
    assert result.featured_activity is not None
    assert result.featured_activity.id_actividad == 10
    assert result.featured_activity_selection_rule is not None
    assert len(result.weeks) == 5
    assert len(result.weeks[0].cells) == 7
    assert result.weeks[0].cells[0].is_padding is True
    assert result.weeks[0].cells[2].day_number == 1
    assert result.weeks[1].cells[4].day_number == 10
    assert result.weeks[1].cells[4].total_actividades == 2
    assert result.weeks[-1].cells[-1].is_padding is True


def test_calendar_service_prepares_admin_scope():
    repository = StubActividadRepository()
    service = ActividadCalendarService(
        repository,
        april_month=4,
        today_provider=lambda: date(2026, 4, 10),
    )

    service.get_calendar_data(ActividadCalendarQuery(user_id=1, role_id=1))

    assert repository.last_query is not None
    assert repository.last_query["include_all_users"] is True


def test_calendar_service_uses_first_activity_when_all_today_are_done():
    repository = StubActividadRepository()
    repository.return_all_done_today = True
    service = ActividadCalendarService(
        repository,
        april_month=4,
        today_provider=lambda: date(2026, 4, 10),
    )

    result = service.get_calendar_data(ActividadCalendarQuery(user_id=2, role_id=2))

    assert result.featured_activity is not None
    assert result.featured_activity.id_actividad == 10
    assert result.featured_activity.realizada is True


def test_calendar_service_skips_featured_activity_when_today_has_no_visible_items():
    repository = StubActividadRepository()
    service = ActividadCalendarService(
        repository,
        april_month=4,
        today_provider=lambda: date(2026, 4, 18),
    )

    result = service.get_calendar_data(ActividadCalendarQuery(user_id=2, role_id=2))

    assert result.featured_activity is None
    assert result.featured_activity_selection_rule is None
