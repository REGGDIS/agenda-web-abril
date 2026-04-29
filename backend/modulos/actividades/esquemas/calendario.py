"""Esquemas de lectura para la vista mensual del calendario."""

from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel


class ActividadCalendarioData(BaseModel):
    """Actividad proyectada a la vista inicial del calendario."""

    id_actividad: int
    titulo: str
    fecha_actividad: date
    hora_inicio: time
    hora_fin: time
    descripcion: str | None = None
    id_categoria: int
    categoria_nombre: str | None = None
    emoji: str | None = None
    realizada: bool
    lugar: str | None = None
    id_usuario: int


class CalendarioDayBlock(BaseModel):
    """Agrupa actividades por dia del mes."""

    fecha: date
    etiqueta_dia: str
    total_actividades: int
    actividades: list[ActividadCalendarioData]


class CalendarioMonthCell(BaseModel):
    """Representa una celda de la grilla mensual."""

    fecha: date | None = None
    day_number: int | None = None
    is_padding: bool
    is_current_month: bool
    total_actividades: int
    actividades: list[ActividadCalendarioData]


class CalendarioWeekRow(BaseModel):
    """Fila semanal dentro de la grilla mensual."""

    week_number: int
    cells: list[CalendarioMonthCell]


class CalendarioDashboardSummary(BaseModel):
    """Metricas compactas para presentar el avance visible del mes."""

    total_actividades: int
    actividades_pendientes: int
    actividades_realizadas: int
    porcentaje_avance: int
    categoria_principal_nombre: str | None = None
    categoria_principal_total: int = 0
    proxima_pendiente_resumen: str | None = None


class CalendarioAbrilData(BaseModel):
    """Resumen del calendario visible para abril."""

    month_label: str
    weekday_labels: list[str]
    visible_for_all_users: bool
    total_actividades: int
    total_dias_con_actividades: int
    dashboard_summary: CalendarioDashboardSummary
    day_blocks: list[CalendarioDayBlock]
    weeks: list[CalendarioWeekRow]
    featured_activity: ActividadCalendarioData | None = None
    featured_activity_selection_rule: str | None = None
    next_pending_activity: ActividadCalendarioData | None = None
    next_pending_activity_selection_rule: str | None = None
    next_pending_activity_countdown_label: str | None = None
    next_pending_activity_starts_at: datetime | None = None
    next_pending_activity_alert_active: bool = False
    next_pending_activity_alert_message: str | None = None


class CalendarioActividadesJsonResponse(BaseModel):
    """Listado plano de actividades visibles para clientes moviles."""

    success: bool
    visible_for_all_users: bool
    total_actividades: int
    actividades: list[ActividadCalendarioData]
