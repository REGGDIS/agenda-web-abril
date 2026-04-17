"""Pruebas de la vista principal del calendario."""

from __future__ import annotations

from datetime import date, datetime, time

from backend.modulos.actividades.esquemas import (
    CalendarioAbrilData,
    CalendarioDayBlock,
    CalendarioWeekRow,
)
from backend.modulos.actividades.servicios import get_actividad_calendar_service
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.esquemas import SesionActualResponse
from backend.modulos.sesiones.servicios import SesionResolutionResult
from backend.tests.conftest import get_client


def test_calendario_redirects_to_login_when_session_is_invalid():
    client = get_client()

    response = client.get("/calendario", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_calendario_renders_logged_user_when_session_is_valid():
    client = get_client()
    client.app.dependency_overrides[get_current_session_result] = lambda: (
        SesionResolutionResult(
            http_status=200,
            response=SesionActualResponse(
                success=True,
                status="session_valid",
                message="Sesion valida.",
                cookie_present=True,
                session_found=True,
                session_active=True,
                ultimo_movimiento_actualizado=True,
                ultimo_movimiento_anterior=datetime(2026, 4, 17, 10, 0, 0),
                sesion={
                    "id_sesion": 7,
                    "id_usuario": 1,
                    "fecha_inicio": datetime(2026, 4, 17, 9, 45, 0),
                    "ultimo_movimiento": datetime(2026, 4, 17, 10, 1, 0),
                    "fecha_cierre": None,
                    "activa": True,
                },
                usuario={
                    "id_usuario": 1,
                    "nombre": "Administrador",
                    "rut": "12.345.678-5",
                    "id_rol": 1,
                    "tema_preferido": "light",
                    "activo": True,
                },
            ),
        )
    )
    client.app.dependency_overrides[get_actividad_calendar_service] = lambda: (
        _FakeActividadCalendarService()
    )

    try:
        response = client.get("/calendario")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Administrador" in response.text
    assert "12.345.678-5" in response.text
    assert "Abril 2026" in response.text
    assert "Lunes" in response.text
    assert "Reunion general" in response.text
    assert "10" in response.text
    assert "Trabajo" in response.text
    assert "Todas las actividades" in response.text
    assert "/calendario/actividades/1/realizada" in response.text
    assert "Pendiente" in response.text


class _FakeActividadCalendarService:
    def get_calendar_data(self, query):
        assert query.user_id == 1
        return CalendarioAbrilData(
            month_label="Abril 2026",
            weekday_labels=[
                "Lunes",
                "Martes",
                "Miercoles",
                "Jueves",
                "Viernes",
                "Sabado",
                "Domingo",
            ],
            visible_for_all_users=True,
            total_actividades=1,
            total_dias_con_actividades=1,
            day_blocks=[
                CalendarioDayBlock(
                    fecha=date(2026, 4, 10),
                    etiqueta_dia="10/04/2026",
                    total_actividades=1,
                    actividades=[
                        {
                            "id_actividad": 1,
                            "titulo": "Reunion general",
                            "fecha_actividad": date(2026, 4, 10),
                            "hora_inicio": time(9, 0),
                            "hora_fin": time(10, 0),
                            "descripcion": "Revision semanal del proyecto.",
                            "categoria_nombre": "Trabajo",
                            "emoji": "📌",
                            "realizada": False,
                            "lugar": "Sala 1",
                            "id_usuario": 1,
                        }
                    ],
                )
            ],
            weeks=[
                CalendarioWeekRow(
                    week_number=1,
                    cells=[
                        {
                            "fecha": None,
                            "day_number": None,
                            "is_padding": True,
                            "is_current_month": False,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": None,
                            "day_number": None,
                            "is_padding": True,
                            "is_current_month": False,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 1),
                            "day_number": 1,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 2),
                            "day_number": 2,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 3),
                            "day_number": 3,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 4),
                            "day_number": 4,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 5),
                            "day_number": 5,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                    ],
                ),
                CalendarioWeekRow(
                    week_number=2,
                    cells=[
                        {
                            "fecha": date(2026, 4, 6),
                            "day_number": 6,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 7),
                            "day_number": 7,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 8),
                            "day_number": 8,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 9),
                            "day_number": 9,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 10),
                            "day_number": 10,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 1,
                            "actividades": [
                                {
                                    "id_actividad": 1,
                                    "titulo": "Reunion general",
                                    "fecha_actividad": date(2026, 4, 10),
                                    "hora_inicio": time(9, 0),
                                    "hora_fin": time(10, 0),
                                    "descripcion": "Revision semanal del proyecto.",
                                    "categoria_nombre": "Trabajo",
                                    "emoji": "📌",
                                    "realizada": False,
                                    "lugar": "Sala 1",
                                    "id_usuario": 1,
                                }
                            ],
                        },
                        {
                            "fecha": date(2026, 4, 11),
                            "day_number": 11,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                        {
                            "fecha": date(2026, 4, 12),
                            "day_number": 12,
                            "is_padding": False,
                            "is_current_month": True,
                            "total_actividades": 0,
                            "actividades": [],
                        },
                    ],
                ),
            ],
        )
