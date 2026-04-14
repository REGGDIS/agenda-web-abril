"""Rutas placeholder para actividades."""

from fastapi import APIRouter


router = APIRouter(prefix="/actividades", tags=["actividades"])


@router.get("/status")
def actividades_status() -> dict[str, str]:
    return {"module": "actividades", "status": "placeholder"}

