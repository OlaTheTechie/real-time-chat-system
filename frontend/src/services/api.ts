import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import {
  AuthResponse,
  User,
  RegisterData,
  LoginData,
  ApiError,
  ChatRoom,
  CreateRoomData,
  Message,
  MessageListResponse,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// flag to prevent multiple refresh attempts
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// request interceptor to inject jwt token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// response interceptor for automatic token refresh on 401
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // if error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // if already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        // no refresh token, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        // attempt to refresh the token
        const response = await axios.post<AuthResponse>(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken }
        );

        const { access_token, refresh_token: newRefreshToken } = response.data;

        // store new tokens
        localStorage.setItem('access_token', access_token);
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken);
        }

        // update authorization header
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }

        processQueue(null, access_token);
        isRefreshing = false;

        // retry original request
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as Error, null);
        isRefreshing = false;

        // refresh failed, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// authentication api functions
export const authApi = {
  register: async (data: RegisterData): Promise<User> => {
    const response = await apiClient.post<User>('/api/v1/auth/register', data);
    return response.data;
  },

  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/api/v1/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/v1/auth/me');
    return response.data;
  },

  requestPasswordReset: async (email: string): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>(
      '/api/v1/auth/password-reset',
      { email }
    );
    return response.data;
  },

  confirmPasswordReset: async (
    token: string,
    newPassword: string
  ): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>(
      '/api/v1/auth/password-reset-confirm',
      { token, new_password: newPassword }
    );
    return response.data;
  },
};

// chat api functions
export const chatApi = {
  getChatRooms: async (): Promise<ChatRoom[]> => {
    const response = await apiClient.get<ChatRoom[]>('/api/v1/chat/rooms');
    return response.data;
  },

  createChatRoom: async (roomData: CreateRoomData): Promise<ChatRoom> => {
    const response = await apiClient.post<ChatRoom>('/api/v1/chat/rooms', roomData);
    return response.data;
  },

  getRoomDetails: async (roomId: number): Promise<ChatRoom> => {
    const response = await apiClient.get<ChatRoom>(`/api/v1/chat/rooms/${roomId}`);
    return response.data;
  },

  getMessages: async (
    roomId: number,
    page: number = 1,
    pageSize: number = 50
  ): Promise<MessageListResponse> => {
    const response = await apiClient.get<MessageListResponse>(
      `/api/v1/chat/rooms/${roomId}/messages`,
      {
        params: { page, page_size: pageSize },
      }
    );
    return response.data;
  },

  sendMessage: async (roomId: number, content: string): Promise<Message> => {
    const response = await apiClient.post<Message>(
      `/api/v1/chat/rooms/${roomId}/messages`,
      { content, message_type: 'text' }
    );
    return response.data;
  },

  getAllUsers: async (): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/api/v1/admin/users', {
      params: { limit: 1000 },
    });
    return response.data;
  },
};

export default apiClient;
