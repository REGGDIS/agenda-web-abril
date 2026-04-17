"""Esquemas para la vista y el resultado de creacion de actividades."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ActividadCreateOptionData(BaseModel):
    """Opcion visible dentro de un selector del formulario."""

    value: int
    label: str


class ActividadCreateFormData(BaseModel):
    """Valores editables del formulario de creacion."""

    titulo: str = ""
    descripcion: str = ""
    fecha_actividad: str = ""
    hora_inicio: str = ""
    hora_fin: str = ""
    emoji: str = ""
    lugar: str = ""
    id_categoria: str = ""
    id_usuario: str = ""
    realizada: bool = False


class ActividadCreateViewData(BaseModel):
    """Datos necesarios para pintar la vista de creacion."""

    form: ActividadCreateFormData = Field(default_factory=ActividadCreateFormData)
    categorias: list[ActividadCreateOptionData] = Field(default_factory=list)
    usuarios: list[ActividadCreateOptionData] = Field(default_factory=list)
    field_errors: dict[str, str] = Field(default_factory=dict)
    general_error: str | None = None
    allow_user_selection: bool = False
    april_range_label: str = "01/04 - 30/04"


class ActividadCreateResult(BaseModel):
    """Resultado minimo de una creacion exitosa."""

    id_actividad: int
    titulo: str
