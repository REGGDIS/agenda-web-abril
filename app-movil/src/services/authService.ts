import { isBackendConfigured } from '../config/environment';
import { apiRequest, buildApiUrl } from './apiClient';
import type { LoginRutResponse, MobileAuthSession } from '../types/auth';

export async function loginWithRut(rut: string): Promise<MobileAuthSession> {
  if (!isBackendConfigured) {
    throw new Error('La URL del backend no esta configurada.');
  }

  const data = await apiRequest<LoginRutResponse>('/auth/login', {
    body: JSON.stringify({ rut }),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });

  if (!data.success || data.status !== 'session_created') {
    throw new Error(data.message || 'No fue posible iniciar sesion.');
  }

  if (!data.usuario || !data.sesion || !data.rut_normalizado) {
    throw new Error('El backend no entrego los datos minimos de sesion.');
  }

  return {
    rutNormalizado: data.rut_normalizado,
    usuario: data.usuario,
    sesion: data.sesion,
  };
}

export async function logoutMobileSession(): Promise<void> {
  if (!isBackendConfigured) {
    return;
  }

  await fetch(buildApiUrl('/sesiones/cerrar'), {
    credentials: 'include',
    method: 'POST',
    redirect: 'manual',
  });
}
