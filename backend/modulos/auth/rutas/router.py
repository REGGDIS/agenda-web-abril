"""Rutas del flujo inicial de autenticacion."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from backend.app.config.settings import get_settings
from backend.modulos.auth.esquemas.login import LoginRutRequest, LoginRutResponse
from backend.modulos.auth.servicios.login_service import AuthService, get_auth_service


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


async def parse_login_payload(request: Request) -> LoginRutRequest:
    """Acepta RUT enviado como JSON o como formulario HTML."""

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
        return LoginRutRequest(**payload)

    form = await request.form()
    return LoginRutRequest(rut=str(form.get("rut", "")))


@router.get("/status")
def auth_status() -> dict[str, str]:
    return {"module": "auth", "status": "login-base-ready"}


@router.post("/login", response_model=LoginRutResponse)
async def login_by_rut(
    payload: LoginRutRequest = Depends(parse_login_payload),
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    """Valida el RUT y prepara el siguiente paso del login."""

    result = auth_service.prepare_login(payload.rut)
    response = JSONResponse(
        status_code=result.http_status,
        content=jsonable_encoder(result.response),
    )
    if result.session_cookie_token:
        response.set_cookie(
            key=settings.session_cookie_name,
            value=result.session_cookie_token,
            httponly=True,
            samesite="lax",
            secure=settings.app_env == "production",
            path="/",
        )
    return response
