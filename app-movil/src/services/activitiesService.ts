import { apiRequest } from './apiClient';
import type {
  ActivitiesResponse,
  Activity,
  ActivityCategoriesResponse,
  ActivityCategory,
  CreateActivityPayload,
  CreateActivityResponse,
  ActivityStatus,
  ActivityStatusUpdateResponse,
  ApiActivity,
  UpdateActivityResponse,
} from '../types/activity';

export async function listAprilActivities(): Promise<Activity[]> {
  const data = await apiRequest<ActivitiesResponse>('/calendario/actividades');

  if (!data.success) {
    throw new Error(data.message || 'No fue posible cargar las actividades.');
  }

  return data.actividades.map(mapApiActivityToActivity);
}

export async function listActivityCategories(): Promise<ActivityCategory[]> {
  const data = await apiRequest<ActivityCategoriesResponse>('/categorias');

  if (!data.success) {
    throw new Error(
      data.message || data.detail || 'No fue posible cargar las categorias.',
    );
  }

  return data.categorias;
}

export async function createActivity(payload: CreateActivityPayload): Promise<number> {
  const data = await apiRequest<CreateActivityResponse>('/actividades/nueva', {
    body: buildFormBody({
      ...payload,
      realizada: payload.realizada ? 'true' : 'false',
    }),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    method: 'POST',
  });

  if (!data.success || typeof data.id_actividad !== 'number') {
    throw new Error(getActivityMutationErrorMessage(data));
  }

  return data.id_actividad;
}

export async function updateActivity(
  activityId: string,
  payload: CreateActivityPayload,
): Promise<number> {
  const data = await apiRequest<UpdateActivityResponse>(
    `/actividades/${activityId}/editar`,
    {
      body: buildFormBody({
        ...payload,
        realizada: payload.realizada ? 'true' : 'false',
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      method: 'POST',
    },
  );

  if (!data.success || typeof data.id_actividad !== 'number') {
    throw new Error(getActivityMutationErrorMessage(data));
  }

  return data.id_actividad;
}

export async function updateActivityStatus(
  activityId: string,
  status: ActivityStatus,
): Promise<ActivityStatus> {
  const realizada = status === 'done';
  const data = await apiRequest<ActivityStatusUpdateResponse>(
    `/calendario/actividades/${activityId}/realizada`,
    {
      body: `realizada=${realizada ? 'true' : 'false'}`,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      method: 'POST',
    },
  );

  if (!data.success || typeof data.realizada !== 'boolean') {
    throw new Error(
      data.message || data.detail || 'No fue posible actualizar la actividad.',
    );
  }

  return data.realizada ? 'done' : 'pending';
}

function buildFormBody(values: Record<string, string | boolean>) {
  return Object.entries(values)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join('&');
}

function getActivityMutationErrorMessage(data: CreateActivityResponse) {
  if (data.field_errors) {
    const firstFieldError = Object.values(data.field_errors)[0];
    if (firstFieldError) {
      return firstFieldError;
    }
  }

  return data.message || data.detail || 'No fue posible guardar la actividad.';
}

function mapApiActivityToActivity(activity: ApiActivity): Activity {
  const placeValue = activity.lugar?.trim() || '';

  return {
    id: String(activity.id_actividad),
    title: activity.titulo,
    description: activity.descripcion,
    date: activity.fecha_actividad,
    dateLabel: formatDateLabel(activity.fecha_actividad),
    startTime: formatTimeLabel(activity.hora_inicio),
    timeLabel: formatTimeLabel(activity.hora_inicio),
    endTime: formatTimeLabel(activity.hora_fin),
    endTimeLabel: formatTimeLabel(activity.hora_fin),
    place: placeValue || 'Sin lugar definido',
    placeValue,
    categoryId: String(activity.id_categoria),
    categoryLabel: activity.categoria_nombre,
    emoji: activity.emoji,
    status: activity.realizada ? 'done' : 'pending',
    userId: String(activity.id_usuario),
  };
}

function formatDateLabel(rawDate: string) {
  const [year, month, day] = rawDate.split('-').map(Number);
  if (!year || !month || !day) {
    return rawDate;
  }

  const date = new Date(year, month - 1, day);
  const weekdayLabels = [
    'Domingo',
    'Lunes',
    'Martes',
    'Miercoles',
    'Jueves',
    'Viernes',
    'Sabado',
  ];
  const monthLabels = [
    'enero',
    'febrero',
    'marzo',
    'abril',
    'mayo',
    'junio',
    'julio',
    'agosto',
    'septiembre',
    'octubre',
    'noviembre',
    'diciembre',
  ];

  return `${weekdayLabels[date.getDay()]} ${day} de ${monthLabels[month - 1]}`;
}

function formatTimeLabel(rawTime: string) {
  const [hours = '', minutes = ''] = rawTime.split(':');
  if (!hours || !minutes) {
    return rawTime;
  }

  return `${hours}:${minutes}`;
}
