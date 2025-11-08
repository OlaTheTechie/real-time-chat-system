import React, { createContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { ChatRoom, Message, CreateRoomData } from '../types';
import { chatApi } from '../services/api';
import { useAuth } from '../hooks/useAuth';

interface ChatContextType {
  rooms: ChatRoom[];
  currentRoom: ChatRoom | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  hasMoreMessages: boolean;
  loadRooms: () => Promise<void>;
  selectRoom: (roomId: number) => Promise<void>;
  createRoom: (roomData: CreateRoomData) => Promise<ChatRoom>;
  loadMessages: (roomId: number, page?: number) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  addMessage: (message: Message) => void;
  clearError: () => void;
}

export const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [currentRoom, setCurrentRoom] = useState<ChatRoom | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMoreMessages, setHasMoreMessages] = useState(false);

  // load rooms when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadRooms();
    } else {
      // clear state when user logs out
      setRooms([]);
      setCurrentRoom(null);
      setMessages([]);
    }
  }, [isAuthenticated]);

  const loadRooms = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const fetchedRooms = await chatApi.getChatRooms();
      setRooms(fetchedRooms);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load chat rooms';
      setError(errorMessage);
      console.error('Error loading rooms:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const selectRoom = useCallback(async (roomId: number) => {
    setIsLoading(true);
    setError(null);
    try {
      // fetch room details
      const roomDetails = await chatApi.getRoomDetails(roomId);
      setCurrentRoom(roomDetails);

      // clear unread count for this room
      setRooms((prevRooms) =>
        prevRooms.map((room) =>
          room.id === roomId ? { ...room, unread_count: 0 } : room
        )
      );

      // load messages for the room
      await loadMessages(roomId);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load room details';
      setError(errorMessage);
      console.error('Error selecting room:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createRoom = useCallback(
    async (roomData: CreateRoomData): Promise<ChatRoom> => {
      setIsLoading(true);
      setError(null);
      try {
        const newRoom = await chatApi.createChatRoom(roomData);
        
        // add new room to the list
        setRooms((prevRooms) => [newRoom, ...prevRooms]);
        
        return newRoom;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || 'Failed to create chat room';
        setError(errorMessage);
        console.error('Error creating room:', err);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const loadMessages = useCallback(async (roomId: number, page: number = 1) => {
    setError(null);
    try {
      const response = await chatApi.getMessages(roomId, page);
      
      if (page === 1) {
        // first page, replace messages
        setMessages(response.messages);
      } else {
        // subsequent pages, prepend older messages
        setMessages((prevMessages) => [...response.messages, ...prevMessages]);
      }
      
      // update hasmore flag from api response
      setHasMoreMessages(response.has_more);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load messages';
      setError(errorMessage);
      console.error('Error loading messages:', err);
    }
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!currentRoom) {
        setError('No room selected');
        return;
      }

      setError(null);
      try {
        const newMessage = await chatApi.sendMessage(currentRoom.id, content);
        
        // add message to the list
        setMessages((prevMessages) => [...prevMessages, newMessage]);

        // update last message in rooms list
        setRooms((prevRooms) =>
          prevRooms.map((room) =>
            room.id === currentRoom.id
              ? { ...room, last_message: newMessage }
              : room
          )
        );
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || 'Failed to send message';
        setError(errorMessage);
        console.error('Error sending message:', err);
        throw err;
      }
    },
    [currentRoom]
  );

  const addMessage = useCallback((message: Message) => {
    console.log('[ChatContext] addMessage called with:', message);
    // check if message already exists to avoid duplicates
    setMessages((prevMessages) => {
      const exists = prevMessages.some((m) => m.id === message.id);
      console.log('[ChatContext] Message exists?', exists, 'Current messages:', prevMessages.length);
      if (exists) {
        return prevMessages;
      }
      console.log('[ChatContext] Adding new message to state');
      return [...prevMessages, message];
    });

    // update last message in rooms list and sort by latest activity
    setRooms((prevRooms) => {
      const updatedRooms = prevRooms.map((room) => {
        if (room.id === message.room_id) {
          // increment unread count if message is from another user and not in current room
          const isCurrentRoom = currentRoom?.id === room.id;
          const isOwnMessage = message.sender_id === user?.id;
          const shouldIncrementUnread = !isCurrentRoom && !isOwnMessage;

          return {
            ...room,
            last_message: message,
            unread_count: shouldIncrementUnread
              ? (room.unread_count || 0) + 1
              : room.unread_count || 0,
          };
        }
        return room;
      });

      // sort rooms by last message timestamp (most recent first)
      return updatedRooms.sort((a, b) => {
        const aTime = a.last_message?.timestamp || a.created_at;
        const bTime = b.last_message?.timestamp || b.created_at;
        return new Date(bTime).getTime() - new Date(aTime).getTime();
      });
    });
  }, [currentRoom, user]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: ChatContextType = {
    rooms,
    currentRoom,
    messages,
    isLoading,
    error,
    hasMoreMessages,
    loadRooms,
    selectRoom,
    createRoom,
    loadMessages,
    sendMessage,
    addMessage,
    clearError,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
