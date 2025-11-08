// user type definition
export interface User {
  id: number;
  email: string;
  username: string;
  is_online: boolean;
  last_seen: string;
  created_at: string;
}

// token type definition
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// registration data
export interface RegisterData {
  email: string;
  username: string;
  password: string;
}

// login data
export interface LoginData {
  email: string;
  password: string;
}

// auth response (combines token and user)
export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user?: User;
}

// api error response
export interface ApiError {
  detail?: string | ValidationError[];
}

// validation error from fastapi
export interface ValidationError {
  type: string;
  loc: (string | number)[];
  msg: string;
  input?: any;
}

// chat-related types

// message type definition
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

// chat room member
export interface ChatRoomMember {
  id: number;
  email: string;
  username: string;
  is_online: boolean;
  last_seen: string;
  joined_at?: string;
  role?: string;
}

// chat room type definition
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

// create room data
export interface CreateRoomData {
  name?: string;
  room_type: 'one_to_one' | 'group';
  member_ids: number[];
}

// message list response with pagination
export interface MessageListResponse {
  messages: Message[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}
