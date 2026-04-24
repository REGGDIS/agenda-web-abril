import { apiRequest } from './apiClient';
import type { ActivitiesResponse, Activity, ApiActivity } from '../types/activity';

export async function listAprilActivities(): Promise<Activity[]> {
  const data = await apiRequest<ActivitiesResponse>('/calendario/actividades');

  if (!data.success) {
    throw new Error(data.message || 'No fue posible cargar las actividades.');
  }

  return data.actividades.map(mapApiActivityToActivity);
}

function mapApiActivityToActivity(activity: ApiActivity): Activity {
  return {
    id: String(activity.id_actividad),
    title: activity.titulo,
    dateLabel: formatDateLabel(activity.fecha_actividad),
    timeLabel: formatTimeLabel(activity.hora_inicio),
    place: activity.lugar?.trim() || 'Sin lugar definido',
    categoryLabel: activity.categoria_nombre,
    emoji: activity.emoji,
    status: activity.realizada ? 'done' : 'pending',
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
