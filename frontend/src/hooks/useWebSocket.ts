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

  // keep refs updated
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  // connect/disconnect based on roomid and token
  useEffect(() => {
    if (!roomId || !token) {
      // disconnect if no roomid or token
      websocketService.disconnect();
      setConnectionStatus('disconnected');
      return;
    }

    // connect to websocket
    websocketService.connect(roomId, token);

    // set up event listeners
    const unsubscribeMessage = websocketService.onMessage((message: Message) => {
      // add message to local state
      setMessages((prev) => [...prev, message]);

      // call external callback if provided
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

    // update initial status
    setConnectionStatus(websocketService.getStatus());

    // cleanup on unmount or when roomid/token changes
    return () => {
      unsubscribeMessage();
      unsubscribeConnect();
      unsubscribeDisconnect();
      unsubscribeError();
      websocketService.disconnect();
      setMessages([]);
    };
  }, [roomId, token]);

  // send message function
  const sendMessage = useCallback(
    (content: string) => {
      if (!content.trim()) {
        return;
      }

      websocketService.sendMessage(content);
    },
    []
  );

  // compute isconnected from status
  const isConnected = connectionStatus === 'connected';

  return {
    sendMessage,
    connectionStatus,
    isConnected,
    messages,
  };
};
