"""Esquemas del modulo actividades."""

from backend.modulos.actividades.esquemas.calendario import (
    ActividadCalendarioData,
    CalendarioActividadesJsonResponse,
    CalendarioAbrilData,
    CalendarioDayBlock,
    CalendarioMonthCell,
    CalendarioWeekRow,
)
from backend.modulos.actividades.esquemas.create import (
    ActividadCreateFormData,
    ActividadCreateOptionData,
    ActividadCreateResult,
    ActividadUpdateResult,
    ActividadCreateViewData,
)
from backend.modulos.actividades.esquemas.detail import ActividadDetalleData

__all__ = [
    "ActividadCalendarioData",
    "ActividadCreateFormData",
    "ActividadCreateOptionData",
    "ActividadCreateResult",
    "ActividadCreateViewData",
    "ActividadUpdateResult",
    "ActividadDetalleData",
    "CalendarioActividadesJsonResponse",
    "CalendarioAbrilData",
    "CalendarioDayBlock",
    "CalendarioMonthCell",
    "CalendarioWeekRow",
]
