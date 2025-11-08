// User type definition
export interface User {
  id: number;
  email: string;
  username: string;
  is_online: boolean;
  last_seen: string;
  created_at: string;
}

// Token type definition
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Registration data
export interface RegisterData {
  email: string;
  username: string;
  password: string;
}

// Login data
export interface LoginData {
  email: string;
  password: string;
}

// Auth response (combines token and user)
export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user?: User;
}

// API error response
export interface ApiError {
  detail: string;
}
