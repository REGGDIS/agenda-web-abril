"""Rutas placeholder para calendario."""

from fastapi import APIRouter


router = APIRouter(prefix="/calendario", tags=["calendario"])


@router.get("/status")
def calendario_status() -> dict[str, str]:
    return {"module": "calendario", "status": "placeholder"}

