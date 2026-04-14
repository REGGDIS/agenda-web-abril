"""Rutas placeholder para sesiones."""

from fastapi import APIRouter


router = APIRouter(prefix="/sesiones", tags=["sesiones"])


@router.get("/status")
def sesiones_status() -> dict[str, str]:
    return {"module": "sesiones", "status": "placeholder"}

