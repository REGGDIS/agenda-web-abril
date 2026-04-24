# Agenda Abril Movil

V1 inicial de la app movil con Expo y TypeScript. La Iteracion 2 conecta el login por RUT con el backend real y mantiene las actividades con datos mock locales.

## Configurar backend para Expo Go

La app no debe usar `127.0.0.1` desde Expo Go porque corre en el telefono. Edita la URL en:

```text
src/config/environment.ts
```

Valor actual:

```ts
backendBaseUrl: 'http://192.168.1.9:8000'
```

Para que el telefono pueda llegar al backend, inicia FastAPI escuchando en la red local:

```bash
uvicorn backend.app.main.app:app --host 0.0.0.0 --port 8000 --reload
```

## Ejecutar

```bash
cd app-movil
npm install
npm start
```

Luego escanea el QR con Expo Go.

## Alcance actual

- Login real contra `POST /auth/login`.
- Pantalla "Mis actividades de abril" con datos locales.
- Navegacion minima por estado dentro de `App.tsx`.
- Configuracion preparada para una futura URL de backend en `src/config/environment.ts`.
