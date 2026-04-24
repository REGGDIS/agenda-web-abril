import { environment } from '../config/environment';

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

  return response.json() as Promise<TResponse>;
}
