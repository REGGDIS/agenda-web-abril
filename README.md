# Agenda Abril

Agenda Abril es una aplicación web y móvil para la gestión de actividades del mes de abril.  
El sistema permite iniciar sesión mediante RUT chileno validado con módulo 11, gestionar actividades, marcarlas como realizadas o pendientes, visualizar información en calendario y acceder a una versión móvil desarrollada con Expo.

El proyecto está desarrollado con una arquitectura modular, manteniendo separación entre backend, frontend web y app móvil.

## Estado actual del proyecto

La aplicación ya cuenta con una versión web funcional y una versión móvil inicial conectada al backend real.

### Funcionalidades principales implementadas

- Login por RUT con validación de módulo 11.
- Sesión persistida en backend.
- Cierre de sesión manual.
- Cierre de sesión por inactividad configurable.
- Control de acceso según usuario autenticado.
- Calendario mensual de abril.
- Listado de actividades reales.
- Creación de actividades.
- Edición de actividades.
- Eliminación de actividades.
- Marcado de actividades como realizadas o pendientes.
- Vista de detalle de actividad.
- Cuenta regresiva de la próxima actividad pendiente.
- Pop-up de actividad destacada del día.
- Alerta sonora una hora antes.
- Modo claro / oscuro.
- Login con imagen estilo Corporate Memphis.
- Logo y favicon de la aplicación.
- Selector simple de emojis por categoría.
- Acceso rápido desde el calendario para crear actividades con fecha precargada.

## Versión móvil

El proyecto incluye una aplicación móvil en Expo ubicada en:

```text
app-movil/
```

La app móvil permite:

- Login real por RUT conectado al backend.
- Carga de actividades reales desde la API.
- Visualización de listado de actividades.
- Vista de detalle de actividad.
- Crear actividades.
- Editar actividades.
- Eliminar actividades.
- Marcar actividades como realizadas o pendientes.
- Cierre de sesión.
- Manejo de sesión expirada.
- Selección simple de emojis.
- Sincronización con la versión web.

## Estructura general

```text
agenda-web-abril/
  backend/
    app/
    modulos/
    tests/

  frontend/
    public/
    src/

  app-movil/
    assets/
    src/
      components/
      config/
      data/
      screens/
      services/
      styles/
      types/

  requirements.txt
  README.md
  .env.example
```

## Tecnologías utilizadas

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic
- Pytest

### Frontend web

- Jinja2 Templates
- HTML
- CSS
- JavaScript

### App móvil

- Expo
- React Native
- TypeScript

## Configuración inicial

### 1. Crear y activar entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación del entorno virtual, se puede usar temporalmente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias del backend

```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copiar el archivo de ejemplo:

```powershell
copy .env.example .env
```

Luego ajustar las credenciales y valores necesarios en `.env`.

Ejemplo de configuración importante:

```env
SESSION_INACTIVITY_MINUTES=3
```

Para una demostración rápida del cierre por inactividad, este valor puede cambiarse temporalmente a:

```env
SESSION_INACTIVITY_MINUTES=1
```

Después de modificar `.env`, se debe reiniciar el backend.

## Ejecutar la aplicación web

Desde la raíz del proyecto:

```powershell
uvicorn backend.app.main.app:app --reload
```

Para que la app móvil pueda conectarse al backend desde Expo Go, iniciar el servidor con:

```powershell
uvicorn backend.app.main.app:app --host 0.0.0.0 --port 8000 --reload
```

La aplicación web queda disponible en:

```text
http://127.0.0.1:8000/login
```

Si se accede desde otro dispositivo en la misma red, se debe usar la IP local del computador, por ejemplo:

```text
http://192.168.X.X:8000/login
```

## Ejecutar la app móvil

Ingresar a la carpeta de la app móvil:

```powershell
cd app-movil
```

Instalar dependencias si es necesario:

```powershell
npm install
```

Ejecutar Expo:

```powershell
npm start
```

Luego escanear el código QR con Expo Go.

Si hay problemas de conexión, se puede intentar:

```powershell
npx expo start -c
```

o:

```powershell
npx expo start --tunnel
```

## Configuración de URL del backend en móvil

La app móvil utiliza una URL base configurada en:

```text
app-movil/src/config/environment.ts
```

Cuando se usa Expo Go en un celular físico, no se debe usar `127.0.0.1`, porque esa dirección apunta al propio teléfono.

Debe usarse la IP local del computador, por ejemplo:

```ts
backendBaseUrl: "http://192.168.X.X:8000";
```

La IP local puede consultarse en Windows con:

```powershell
ipconfig
```

## Pruebas

Ejecutar la suite de pruebas del backend:

```powershell
pytest backend/tests
```

También se pueden ejecutar pruebas puntuales por módulo, por ejemplo:

```powershell
pytest backend/tests/unit/calendario
```

En la app móvil, verificar TypeScript con:

```powershell
cd app-movil
npx tsc --noEmit
```

## Notas importantes

- No subir el archivo `.env` al repositorio.
- Usar `.env.example` para documentar variables necesarias.
- La aplicación trabaja solo con actividades del mes de abril.
- El cierre por inactividad es configurable mediante `SESSION_INACTIVITY_MINUTES`.
- La versión móvil depende de que el backend esté encendido y accesible desde la misma red o mediante túnel.
- La app móvil usa Expo Go para pruebas en dispositivo físico.

## Alcance actual

El proyecto cuenta con una versión web funcional y una versión móvil inicial avanzada.  
La versión móvil ya permite realizar las operaciones principales sobre actividades, conectándose al backend real.

## Posibles mejoras futuras

- Calendario mensual visual en la app móvil.
- Persistencia local de sesión móvil.
- Mejoras de diseño responsive.
- Notificaciones móviles.
- Sincronización más avanzada de preferencias visuales.
