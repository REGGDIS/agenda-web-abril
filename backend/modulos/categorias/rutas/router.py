"""Rutas placeholder para categorias."""

from fastapi import APIRouter


router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("/status")
def categorias_status() -> dict[str, str]:
    return {"module": "categorias", "status": "placeholder"}

