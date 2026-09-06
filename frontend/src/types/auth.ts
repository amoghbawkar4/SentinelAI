export interface User {
  id: string;
  name: string;
  email: string;
  role_id: number;
  role_name: string;
  is_verified: boolean;
  is_active: boolean;
  last_login?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
  login_as?: string;
  portal: 'employee' | 'administrator';
  remember_me?: boolean;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
