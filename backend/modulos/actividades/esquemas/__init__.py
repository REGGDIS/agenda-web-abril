"""Esquemas del modulo actividades."""

from backend.modulos.actividades.esquemas.calendario import (
    ActividadCalendarioData,
    CalendarioAbrilData,
    CalendarioDayBlock,
    CalendarioMonthCell,
    CalendarioWeekRow,
)
from backend.modulos.actividades.esquemas.create import (
    ActividadCreateFormData,
    ActividadCreateOptionData,
    ActividadCreateResult,
    ActividadCreateViewData,
)
from backend.modulos.actividades.esquemas.detail import ActividadDetalleData

__all__ = [
    "ActividadCalendarioData",
    "ActividadCreateFormData",
    "ActividadCreateOptionData",
    "ActividadCreateResult",
    "ActividadCreateViewData",
    "ActividadDetalleData",
    "CalendarioAbrilData",
    "CalendarioDayBlock",
    "CalendarioMonthCell",
    "CalendarioWeekRow",
]
