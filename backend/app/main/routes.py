"""Rutas generales del proyecto."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.app.config.settings import get_settings


settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "project": "Agenda Abril"}


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse(url="/calendario", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="modulos/auth/templates/login.html",
        context={
            "request": request,
            "app_name": settings.app_name,
            "page_title": "Ingreso al sistema",
            "hide_primary_navigation": True,
        },
    )
