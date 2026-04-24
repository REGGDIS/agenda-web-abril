import type { Activity } from '../types/activity';

export const mockActivities: Activity[] = [
  {
    id: 'act-01',
    title: 'Reunion de coordinacion',
    dateLabel: 'Lunes 8 de abril',
    timeLabel: '09:30',
    place: 'Sala principal',
    status: 'pending',
  },
  {
    id: 'act-02',
    title: 'Revision de checklist semanal',
    dateLabel: 'Jueves 11 de abril',
    timeLabel: '12:00',
    place: 'Oficina central',
    status: 'done',
  },
  {
    id: 'act-03',
    title: 'Preparar actividad comunitaria',
    dateLabel: 'Martes 16 de abril',
    timeLabel: '15:45',
    place: 'Centro de actividades',
    status: 'pending',
  },
];
