"""Esquemas del modulo actividades."""

from backend.modulos.actividades.esquemas.calendario import (
    ActividadCalendarioData,
    CalendarioAbrilData,
    CalendarioDayBlock,
    CalendarioMonthCell,
    CalendarioWeekRow,
)
from backend.modulos.actividades.esquemas.detail import ActividadDetalleData

__all__ = [
    "ActividadCalendarioData",
    "ActividadDetalleData",
    "CalendarioAbrilData",
    "CalendarioDayBlock",
    "CalendarioMonthCell",
    "CalendarioWeekRow",
]
