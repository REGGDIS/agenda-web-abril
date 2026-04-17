"""Servicio de lectura de actividades para la vista del calendario."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from itertools import groupby
from typing import Protocol

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings
from backend.app.db.session import get_db
from backend.modulos.actividades.esquemas import (
    ActividadCalendarioData,
    CalendarioAbrilData,
    CalendarioDayBlock,
    CalendarioMonthCell,
    CalendarioWeekRow,
)
from backend.modulos.actividades.modelos import Actividad
from backend.modulos.actividades.repositorios import SqlAlchemyActividadRepository


ADMIN_ROLE_ID = 1
WEEKDAY_LABELS = [
    "Lunes",
    "Martes",
    "Miercoles",
    "Jueves",
    "Viernes",
    "Sabado",
    "Domingo",
]


class ActividadCalendarRepository(Protocol):
    """Contrato minimo para consultar actividades del calendario."""

    def list_april_activities_for_calendar(
        self,
        *,
        user_id: int,
        include_all_users: bool,
        april_month: int,
    ) -> list[Actividad]:
        """Obtiene actividades de abril para la vista inicial."""


@dataclass(frozen=True)
class ActividadCalendarQuery:
    """Consulta necesaria para proyectar actividades al calendario."""

    user_id: int
    role_id: int

    @property
    def include_all_users(self) -> bool:
        # En esta etapa se usa la convención inicial del proyecto:
        # el rol administrador corresponde al id_rol=1.
        return self.role_id == ADMIN_ROLE_ID


class ActividadCalendarService:
    """Agrupa actividades de abril para una vista visible y simple."""

    def __init__(
        self,
        actividad_repository: ActividadCalendarRepository,
        *,
        april_month: int,
    ) -> None:
        self._actividad_repository = actividad_repository
        self._april_month = april_month

    def get_calendar_data(self, query: ActividadCalendarQuery) -> CalendarioAbrilData:
        actividades = self._actividad_repository.list_april_activities_for_calendar(
            user_id=query.user_id,
            include_all_users=query.include_all_users,
            april_month=self._april_month,
        )

        projected_activities = [
            self._build_activity_data(actividad) for actividad in actividades
        ]
        activities_by_date = self._group_projected_activities_by_date(projected_activities)
        day_blocks: list[CalendarioDayBlock] = []
        for fecha, grouped_activities in groupby(
            projected_activities,
            key=lambda actividad: actividad.fecha_actividad,
        ):
            activity_cards = list(grouped_activities)
            day_blocks.append(
                CalendarioDayBlock(
                    fecha=fecha,
                    etiqueta_dia=self._build_day_label(fecha),
                    total_actividades=len(activity_cards),
                    actividades=activity_cards,
                )
            )

        reference_year = self._resolve_reference_year(actividades)
        weeks = self._build_month_weeks(
            reference_year=reference_year,
            activities_by_date=activities_by_date,
        )

        return CalendarioAbrilData(
            month_label=f"Abril {reference_year}",
            weekday_labels=WEEKDAY_LABELS,
            visible_for_all_users=query.include_all_users,
            total_actividades=len(actividades),
            total_dias_con_actividades=len(day_blocks),
            day_blocks=day_blocks,
            weeks=weeks,
        )

    @staticmethod
    def _build_day_label(fecha: date) -> str:
        return f"{fecha.day:02d}/{fecha.month:02d}/{fecha.year}"

    @staticmethod
    def _build_activity_data(actividad: Actividad) -> ActividadCalendarioData:
        categoria_nombre = None
        if actividad.categoria is not None:
            categoria_nombre = actividad.categoria.nombre_categoria

        return ActividadCalendarioData(
            id_actividad=actividad.id_actividad,
            titulo=actividad.titulo,
            fecha_actividad=actividad.fecha_actividad,
            hora_inicio=actividad.hora_inicio,
            hora_fin=actividad.hora_fin,
            descripcion=actividad.descripcion,
            categoria_nombre=categoria_nombre,
            emoji=actividad.emoji,
            realizada=actividad.realizada,
            lugar=actividad.lugar,
            id_usuario=actividad.id_usuario,
        )

    @staticmethod
    def _group_projected_activities_by_date(
        projected_activities: list[ActividadCalendarioData],
    ) -> dict[date, list[ActividadCalendarioData]]:
        grouped: dict[date, list[ActividadCalendarioData]] = {}
        for actividad in projected_activities:
            grouped.setdefault(actividad.fecha_actividad, []).append(actividad)
        return grouped

    @staticmethod
    def _resolve_reference_year(actividades: list[Actividad]) -> int:
        if actividades:
            return actividades[0].fecha_actividad.year
        return date.today().year

    def _build_month_weeks(
        self,
        *,
        reference_year: int,
        activities_by_date: dict[date, list[ActividadCalendarioData]],
    ) -> list[CalendarioWeekRow]:
        month_matrix = calendar.Calendar(firstweekday=0).monthdatescalendar(
            reference_year,
            self._april_month,
        )
        weeks: list[CalendarioWeekRow] = []

        for week_index, week_dates in enumerate(month_matrix, start=1):
            cells: list[CalendarioMonthCell] = []
            for current_date in week_dates:
                is_current_month = current_date.month == self._april_month
                activities = activities_by_date.get(current_date, []) if is_current_month else []
                cells.append(
                    CalendarioMonthCell(
                        fecha=current_date if is_current_month else None,
                        day_number=current_date.day if is_current_month else None,
                        is_padding=not is_current_month,
                        is_current_month=is_current_month,
                        total_actividades=len(activities),
                        actividades=activities,
                    )
                )

            weeks.append(CalendarioWeekRow(week_number=week_index, cells=cells))

        return weeks


def get_actividad_calendar_service(
    db: Session = Depends(get_db),
) -> ActividadCalendarService:
    """Fabrica del servicio de calendario para actividades."""

    settings = get_settings()
    actividad_repository = SqlAlchemyActividadRepository(db)
    return ActividadCalendarService(
        actividad_repository,
        april_month=settings.april_month,
    )
