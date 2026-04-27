"""Rutas del modulo categorias."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings
from backend.app.db.session import get_db
from backend.modulos.categorias.repositorios import SqlAlchemyCategoriaRepository
from backend.modulos.sesiones.dependencias import get_current_session_result
from backend.modulos.sesiones.servicios import SesionResolutionResult


router = APIRouter(prefix="/categorias", tags=["categorias"])
settings = get_settings()


@router.get("/status")
def categorias_status() -> dict[str, str]:
    return {"module": "categorias", "status": "placeholder"}


def get_categoria_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCategoriaRepository:
    return SqlAlchemyCategoriaRepository(db)


@router.get("")
@router.get("/")
def categorias_json(
    session_result: SesionResolutionResult = Depends(get_current_session_result),
    categoria_repository: SqlAlchemyCategoriaRepository = Depends(
        get_categoria_repository
    ),
) -> JSONResponse:
    """Entrega categorias reales para formularios moviles."""

    if (
        not session_result.response.success
        or session_result.response.usuario is None
        or session_result.response.sesion is None
    ):
        response = JSONResponse(
            status_code=session_result.http_status,
            content=jsonable_encoder(
                {
                    "success": False,
                    "status": session_result.response.status,
                    "message": session_result.response.message,
                    "categorias": [],
                }
            ),
        )
        response.delete_cookie(key=settings.session_cookie_name, path="/")
        return response

    categorias = categoria_repository.list_all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            {
                "success": True,
                "categorias": [
                    {
                        "id_categoria": categoria.id_categoria,
                        "nombre_categoria": categoria.nombre_categoria,
                    }
                    for categoria in categorias
                ],
            }
        ),
    )
