"""Instancia principal de FastAPI para Agenda Abril."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.config.settings import get_settings
from backend.app.main.routes import router as main_router
from backend.modulos.actividades.rutas.router import router as actividades_router
from backend.modulos.alertas.rutas.router import router as alertas_router
from backend.modulos.auth.rutas.router import router as auth_router
from backend.modulos.calendario.rutas.router import router as calendario_router
from backend.modulos.categorias.rutas.router import router as categorias_router
from backend.modulos.roles.rutas.router import router as roles_router
from backend.modulos.sesiones.rutas.router import router as sesiones_router
from backend.modulos.tema.rutas.router import router as tema_router
from backend.modulos.usuarios.rutas.router import router as usuarios_router


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
    )

    app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

    app.include_router(main_router)
    app.include_router(auth_router)
    app.include_router(usuarios_router)
    app.include_router(roles_router)
    app.include_router(actividades_router)
    app.include_router(categorias_router)
    app.include_router(alertas_router)
    app.include_router(sesiones_router)
    app.include_router(calendario_router)
    app.include_router(tema_router)

    return app


app = create_app()

