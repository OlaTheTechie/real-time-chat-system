import { useEffect, useState, useCallback, useRef } from 'react';
import { Message } from '../types';
import { websocketService, ConnectionStatus } from '../services/websocket';

interface UseWebSocketOptions {
  roomId: number | null;
  token: string | null;
  onMessage?: (message: Message) => void;
  onError?: (error: Error) => void;
}

interface UseWebSocketReturn {
  sendMessage: (content: string) => void;
  connectionStatus: ConnectionStatus;
  isConnected: boolean;
  messages: Message[];
}

/**
 * Custom hook for managing WebSocket connections
 */
export const useWebSocket = ({
  roomId,
  token,
  onMessage,
  onError,
}: UseWebSocketOptions): UseWebSocketReturn => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [messages, setMessages] = useState<Message[]>([]);
  const onMessageRef = useRef(onMessage);
  const onErrorRef = useRef(onError);

  // Keep refs updated
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  // Connect/disconnect based on roomId and token
  useEffect(() => {
    if (!roomId || !token) {
      // Disconnect if no roomId or token
      websocketService.disconnect();
      setConnectionStatus('disconnected');
      return;
    }

    // Connect to WebSocket
    websocketService.connect(roomId, token);

    // Set up event listeners
    const unsubscribeMessage = websocketService.onMessage((message: Message) => {
      // Add message to local state
      setMessages((prev) => [...prev, message]);

      // Call external callback if provided
      if (onMessageRef.current) {
        onMessageRef.current(message);
      }
    });

    const unsubscribeConnect = websocketService.onConnect((status: ConnectionStatus) => {
      setConnectionStatus(status);
    });

    const unsubscribeDisconnect = websocketService.onDisconnect((status: ConnectionStatus) => {
      setConnectionStatus(status);
    });

    const unsubscribeError = websocketService.onError((error: Error) => {
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
    });

    // Update initial status
    setConnectionStatus(websocketService.getStatus());

    // Cleanup on unmount or when roomId/token changes
    return () => {
      unsubscribeMessage();
      unsubscribeConnect();
      unsubscribeDisconnect();
      unsubscribeError();
      websocketService.disconnect();
      setMessages([]);
    };
  }, [roomId, token]);

  // Send message function
  const sendMessage = useCallback(
    (content: string) => {
      if (!content.trim()) {
        return;
      }

      websocketService.sendMessage(content);
    },
    []
  );

  // Compute isConnected from status
  const isConnected = connectionStatus === 'connected';

  return {
    sendMessage,
    connectionStatus,
    isConnected,
    messages,
  };
};
