"""Rutas placeholder para tema."""

from fastapi import APIRouter


router = APIRouter(prefix="/tema", tags=["tema"])


@router.get("/status")
def tema_status() -> dict[str, str]:
    return {"module": "tema", "status": "placeholder"}

