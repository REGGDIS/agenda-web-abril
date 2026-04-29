"""Servicio de lectura de actividades para la vista del calendario."""

from __future__ import annotations

import calendar
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from itertools import groupby
from typing import Callable, Protocol

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings
from backend.app.db.session import get_db
from backend.modulos.actividades.esquemas import (
    ActividadCalendarioData,
    CalendarioAbrilData,
    CalendarioDashboardSummary,
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
        today_provider: Callable[[], date] | None = None,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._actividad_repository = actividad_repository
        self._april_month = april_month
        self._today_provider = today_provider or date.today
        self._now_provider = now_provider or datetime.now

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
        current_moment = self._now_provider()
        featured_activity = self._select_featured_activity_for_today(projected_activities)
        next_pending_activity = self._select_next_pending_activity(
            projected_activities,
            current_moment=current_moment,
        )
        next_pending_activity_starts_at = None
        next_pending_activity_countdown_label = None
        next_pending_activity_alert_active = False
        next_pending_activity_alert_message = None
        if next_pending_activity is not None:
            next_pending_activity_starts_at = datetime.combine(
                next_pending_activity.fecha_actividad,
                next_pending_activity.hora_inicio,
            )
            remaining_time = next_pending_activity_starts_at - current_moment
            next_pending_activity_countdown_label = self._build_countdown_label(
                remaining_time
            )
            next_pending_activity_alert_active = self._is_alert_window_active(
                remaining_time
            )
            if next_pending_activity_alert_active:
                next_pending_activity_alert_message = (
                    "Comienza en menos de una hora. Alerta sonora habilitada para esta pagina."
                )

        return CalendarioAbrilData(
            month_label=f"Abril {reference_year}",
            weekday_labels=WEEKDAY_LABELS,
            visible_for_all_users=query.include_all_users,
            total_actividades=len(actividades),
            total_dias_con_actividades=len(day_blocks),
            dashboard_summary=self._build_dashboard_summary(
                projected_activities=projected_activities,
                next_pending_activity=next_pending_activity,
            ),
            day_blocks=day_blocks,
            weeks=weeks,
            featured_activity=featured_activity,
            featured_activity_selection_rule=(
                "Se destaca la primera actividad pendiente del dia ordenada por hora. "
                "Si todas ya estan realizadas, se muestra la primera actividad del dia."
            )
            if featured_activity is not None
            else None,
            next_pending_activity=next_pending_activity,
            next_pending_activity_selection_rule=(
                "Se selecciona la actividad pendiente futura mas cercana por fecha y hora de inicio."
            )
            if next_pending_activity is not None
            else None,
            next_pending_activity_countdown_label=next_pending_activity_countdown_label,
            next_pending_activity_starts_at=next_pending_activity_starts_at,
            next_pending_activity_alert_active=next_pending_activity_alert_active,
            next_pending_activity_alert_message=next_pending_activity_alert_message,
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
            id_categoria=actividad.id_categoria,
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
    def _build_dashboard_summary(
        *,
        projected_activities: list[ActividadCalendarioData],
        next_pending_activity: ActividadCalendarioData | None,
    ) -> CalendarioDashboardSummary:
        total_actividades = len(projected_activities)
        actividades_realizadas = sum(
            1 for actividad in projected_activities if actividad.realizada
        )
        actividades_pendientes = total_actividades - actividades_realizadas
        porcentaje_avance = (
            round((actividades_realizadas / total_actividades) * 100)
            if total_actividades
            else 0
        )

        category_counter = Counter(
            actividad.categoria_nombre or "Sin categoria"
            for actividad in projected_activities
        )
        categoria_principal_nombre = None
        categoria_principal_total = 0
        if category_counter:
            categoria_principal_nombre, categoria_principal_total = sorted(
                category_counter.items(),
                key=lambda item: (-item[1], item[0]),
            )[0]

        proxima_pendiente_resumen = None
        if next_pending_activity is not None:
            proxima_pendiente_resumen = (
                f"{next_pending_activity.fecha_actividad.strftime('%d/%m')} "
                f"{next_pending_activity.hora_inicio.strftime('%H:%M')} - "
                f"{next_pending_activity.titulo}"
            )

        return CalendarioDashboardSummary(
            total_actividades=total_actividades,
            actividades_pendientes=actividades_pendientes,
            actividades_realizadas=actividades_realizadas,
            porcentaje_avance=porcentaje_avance,
            categoria_principal_nombre=categoria_principal_nombre,
            categoria_principal_total=categoria_principal_total,
            proxima_pendiente_resumen=proxima_pendiente_resumen,
        )

    @staticmethod
    def _resolve_reference_year(actividades: list[Actividad]) -> int:
        if actividades:
            return actividades[0].fecha_actividad.year
        return date.today().year

    def _select_featured_activity_for_today(
        self,
        projected_activities: list[ActividadCalendarioData],
    ) -> ActividadCalendarioData | None:
        today = self._today_provider()
        if today.month != self._april_month:
            return None

        todays_activities = [
            actividad
            for actividad in projected_activities
            if actividad.fecha_actividad == today
        ]
        if not todays_activities:
            return None

        pending_activities = [
            actividad for actividad in todays_activities if not actividad.realizada
        ]
        if pending_activities:
            return pending_activities[0]

        return todays_activities[0]

    def _select_next_pending_activity(
        self,
        projected_activities: list[ActividadCalendarioData],
        *,
        current_moment: datetime,
    ) -> ActividadCalendarioData | None:
        future_pending_activities = [
            actividad
            for actividad in projected_activities
            if not actividad.realizada
            and datetime.combine(
                actividad.fecha_actividad,
                actividad.hora_inicio,
            )
            > current_moment
        ]
        if not future_pending_activities:
            return None

        future_pending_activities.sort(
            key=lambda actividad: (
                actividad.fecha_actividad,
                actividad.hora_inicio,
                actividad.id_actividad,
            )
        )
        return future_pending_activities[0]

    @staticmethod
    def _build_countdown_label(remaining_time: timedelta) -> str:
        total_seconds = max(int(remaining_time.total_seconds()), 0)
        if total_seconds < 60:
            return "Comienza en menos de un minuto."

        total_minutes = total_seconds // 60
        days, remaining_minutes = divmod(total_minutes, 60 * 24)
        hours, minutes = divmod(remaining_minutes, 60)

        parts: list[str] = []
        if days:
            parts.append(f"{days} dia" if days == 1 else f"{days} dias")
        if hours:
            parts.append(f"{hours} hora" if hours == 1 else f"{hours} horas")
        if minutes:
            parts.append(f"{minutes} minuto" if minutes == 1 else f"{minutes} minutos")

        if not parts:
            return "Comienza en menos de un minuto."
        if len(parts) == 1:
            prefix = "Falta" if parts[0].startswith("1 ") else "Faltan"
            return f"{prefix} {parts[0]}."
        if len(parts) == 2:
            return f"Faltan {parts[0]} y {parts[1]}."

        return f"Faltan {parts[0]}, {parts[1]} y {parts[2]}."

    @staticmethod
    def _is_alert_window_active(remaining_time: timedelta) -> bool:
        return timedelta(0) < remaining_time <= timedelta(hours=1)

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
