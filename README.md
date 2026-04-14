# Agenda Abril

Esqueleto inicial del proyecto web "Agenda Abril" basado en FastAPI, Jinja2,
SQLAlchemy, Alembic y PostgreSQL.

## Alcance de esta etapa

- Estructura física inicial del proyecto.
- Configuracion minima de backend y plantillas.
- Placeholders de modulos y rutas.
- Base de conexion a PostgreSQL y migraciones.
- Recursos estaticos y documentacion inicial.

## No incluido todavia

- Login funcional completo por RUT.
- CRUD completo de actividades.
- Alertas reales, countdown o popup funcional.
- Reglas de negocio completas.

## Ejecucion prevista

1. Crear y activar un entorno virtual.
2. Instalar dependencias con `pip install -r requirements.txt`.
3. Copiar `.env.example` a `.env` y ajustar credenciales.
4. Iniciar con `uvicorn backend.app.main.app:app --reload`.

