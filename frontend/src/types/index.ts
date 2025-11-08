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

// Chat-related types

// Message type definition
export interface Message {
  id: number;
  room_id: number;
  sender_id: number;
  content: string;
  timestamp: string;
  message_type: string;
  is_edited: boolean;
  sender_username?: string;
}

// Chat room member
export interface ChatRoomMember {
  id: number;
  email: string;
  username: string;
  is_online: boolean;
  last_seen: string;
  joined_at?: string;
  role?: string;
}

// Chat room type definition
export interface ChatRoom {
  id: number;
  name: string | null;
  room_type: 'one_to_one' | 'group';
  created_by: number;
  created_at: string;
  members: ChatRoomMember[];
  last_message?: Message;
  unread_count?: number;
}

// Create room data
export interface CreateRoomData {
  name?: string;
  room_type: 'one_to_one' | 'group';
  member_ids: number[];
}

// Message list response with pagination
export interface MessageListResponse {
  messages: Message[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}
