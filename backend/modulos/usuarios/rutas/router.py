"""Rutas placeholder para usuarios."""

from fastapi import APIRouter


router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/status")
def usuarios_status() -> dict[str, str]:
    return {"module": "usuarios", "status": "placeholder"}

