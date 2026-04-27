import { environment } from '../config/environment';

const INVALID_SESSION_STATUSES = new Set([
  'cookie_missing',
  'session_expired',
  'session_inactive',
  'session_not_found',
]);

export class MobileSessionExpiredError extends Error {
  constructor() {
    super('Tu sesión expiró. Ingresa nuevamente.');
    this.name = 'MobileSessionExpiredError';
  }
}

export function isMobileSessionExpiredError(
  error: unknown,
): error is MobileSessionExpiredError {
  return error instanceof MobileSessionExpiredError;
}

export function getBackendBaseUrl() {
  return environment.backendBaseUrl;
}

export function buildApiUrl(path: string) {
  const baseUrl = getBackendBaseUrl().replace(/\/$/, '');
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  return `${baseUrl}${normalizedPath}`;
}

export async function apiRequest<TResponse>(
  path: string,
  options: RequestInit = {},
): Promise<TResponse> {
  const response = await fetch(buildApiUrl(path), {
    credentials: 'include',
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.headers ?? {}),
    },
  });

  const contentType = response.headers.get('content-type') ?? '';
  if (!contentType.includes('application/json')) {
    throw new Error('El backend no respondio con JSON.');
  }

  const data = await response.json();
  if (isInvalidSessionResponse(response.status, data)) {
    throw new MobileSessionExpiredError();
  }

  return data as TResponse;
}

function isInvalidSessionResponse(statusCode: number, data: unknown) {
  if (statusCode === 401) {
    return true;
  }

  if (!data || typeof data !== 'object' || !('status' in data)) {
    return false;
  }

  const responseStatus = (data as { status?: unknown }).status;
  return (
    typeof responseStatus === 'string' &&
    INVALID_SESSION_STATUSES.has(responseStatus)
  );
}
