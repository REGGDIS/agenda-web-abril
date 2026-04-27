export type LoginStatus =
  | 'validation_error'
  | 'access_denied'
  | 'user_inactive'
  | 'session_created';

export type NextLoginStep =
  | 'corregir_rut'
  | 'acceso_denegado'
  | 'reactivar_usuario'
  | 'validar_sesion_activa';

export type LoginUser = {
  id_usuario: number;
  nombre: string;
  rut: string;
  id_rol: number;
  tema_preferido: string | null;
  activo: boolean;
};

export type LoginSession = {
  id_sesion: number;
  id_usuario: number;
  fecha_inicio: string;
  ultimo_movimiento: string;
  activa: boolean;
};

export type LoginRutResponse = {
  success: boolean;
  status: LoginStatus;
  message: string;
  rut_ingresado: string;
  rut_normalizado: string | null;
  usuario_existe: boolean;
  usuario: LoginUser | null;
  sesion: LoginSession | null;
  siguiente_paso: NextLoginStep;
};

export type MobileAuthSession = {
  rutNormalizado: string;
  usuario: LoginUser;
  sesion: LoginSession;
};

export type SessionActivityResponse = {
  success: boolean;
  status: string;
  message: string;
};
