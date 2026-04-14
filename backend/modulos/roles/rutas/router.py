"""Rutas placeholder para roles."""

from fastapi import APIRouter


router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/status")
def roles_status() -> dict[str, str]:
    return {"module": "roles", "status": "placeholder"}

