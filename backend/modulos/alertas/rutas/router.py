"""Rutas placeholder para alertas."""

from fastapi import APIRouter


router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("/status")
def alertas_status() -> dict[str, str]:
    return {"module": "alertas", "status": "placeholder"}

