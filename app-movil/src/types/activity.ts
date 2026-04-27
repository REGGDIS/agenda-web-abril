export type ActivityStatus = 'pending' | 'done';

export type Activity = {
  id: string;
  title: string;
  description: string | null;
  date: string;
  dateLabel: string;
  startTime: string;
  timeLabel: string;
  endTime: string;
  endTimeLabel: string;
  place: string;
  placeValue: string;
  categoryId: string;
  categoryLabel: string | null;
  emoji: string | null;
  status: ActivityStatus;
  userId: string;
};

export type ApiActivity = {
  id_actividad: number;
  titulo: string;
  fecha_actividad: string;
  hora_inicio: string;
  hora_fin: string;
  descripcion: string | null;
  id_categoria: number;
  categoria_nombre: string | null;
  emoji: string | null;
  realizada: boolean;
  lugar: string | null;
  id_usuario: number;
};

export type ActivitiesResponse = {
  success: boolean;
  visible_for_all_users: boolean;
  total_actividades: number;
  actividades: ApiActivity[];
  message?: string;
};

export type ActivityCategory = {
  id_categoria: number;
  nombre_categoria: string;
};

export type ActivityCategoriesResponse = {
  success: boolean;
  categorias: ActivityCategory[];
  message?: string;
  detail?: string;
};

export type CreateActivityPayload = {
  titulo: string;
  descripcion: string;
  fecha_actividad: string;
  hora_inicio: string;
  hora_fin: string;
  id_categoria: string;
  id_usuario: string;
  emoji: string;
  lugar: string;
  realizada: boolean;
};

export type CreateActivityResponse = {
  success: boolean;
  message?: string;
  id_actividad?: number;
  titulo?: string;
  field_errors?: Record<string, string>;
  detail?: string;
};

export type UpdateActivityResponse = CreateActivityResponse;

export type ActivityStatusUpdateResponse = {
  success: boolean;
  message?: string;
  id_actividad?: number;
  realizada?: boolean;
  detail?: string;
};
