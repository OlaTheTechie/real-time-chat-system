import { Message } from '../types';

// WebSocket message types
export interface WebSocketMessage {
  type: 'message' | 'typing' | 'user_joined' | 'user_left' | 'error';
  data: Message | any;
}

// Connection status
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

// Event callback types
type MessageCallback = (message: Message) => void;
type StatusCallback = (status: ConnectionStatus) => void;
type ErrorCallback = (error: Error) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private roomId: number | null = null;
  private token: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private reconnectTimer: NodeJS.Timeout | null = null;
  private messageQueue: string[] = [];
  private isIntentionalClose = false;

  // Event listeners
  private messageListeners: MessageCallback[] = [];
  private connectListeners: StatusCallback[] = [];
  private disconnectListeners: StatusCallback[] = [];
  private errorListeners: ErrorCallback[] = [];

  constructor() {
    // Bind methods to ensure correct 'this' context
    this.handleOpen = this.handleOpen.bind(this);
    this.handleMessage = this.handleMessage.bind(this);
    this.handleError = this.handleError.bind(this);
    this.handleClose = this.handleClose.bind(this);
  }

  /**
   * Connect to a chat room WebSocket
   */
  connect(roomId: number, token: string): void {
    // If already connected to the same room, don't reconnect
    if (this.ws && this.roomId === roomId && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    // Close existing connection if any
    if (this.ws) {
      this.disconnect();
    }

    this.roomId = roomId;
    this.token = token;
    this.isIntentionalClose = false;
    this.reconnectAttempts = 0;

    this.createWebSocket();
  }

  /**
   * Create WebSocket connection
   */
  private createWebSocket(): void {
    if (!this.roomId || !this.token) {
      console.error('Cannot create WebSocket: missing roomId or token');
      return;
    }

    const wsBaseUrl = process.env.REACT_APP_WS_BASE_URL || 'ws://localhost:8000';
    const wsUrl = `${wsBaseUrl}/ws/chat/${this.roomId}?token=${this.token}`;

    try {
      this.notifyStatusChange('connecting');
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = this.handleOpen;
      this.ws.onmessage = this.handleMessage;
      this.ws.onerror = this.handleError;
      this.ws.onclose = this.handleClose;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.notifyError(error as Error);
      this.attemptReconnect();
    }
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    console.log(`WebSocket connected to room ${this.roomId}`);
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    this.notifyStatusChange('connected');

    // Send queued messages
    this.flushMessageQueue();
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);

      // Handle different message types
      if (data.type === 'message' && data.data) {
        const message: Message = data.data;
        this.notifyMessage(message);
      } else if (data.type === 'error') {
        console.error('WebSocket error message:', data.data);
        this.notifyError(new Error(data.data.message || 'WebSocket error'));
      }
      // Handle other message types (typing, user_joined, user_left) if needed
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  /**
   * Handle WebSocket error event
   */
  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.notifyStatusChange('error');
    this.notifyError(new Error('WebSocket connection error'));
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(event: CloseEvent): void {
    console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
    this.notifyStatusChange('disconnected');

    // Attempt reconnection if not intentionally closed
    if (!this.isIntentionalClose && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.attemptReconnect();
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);

    console.log(
      `Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`
    );

    this.reconnectTimer = setTimeout(() => {
      if (this.roomId && this.token) {
        this.createWebSocket();
      }
    }, delay);
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    this.isIntentionalClose = true;

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onerror = null;
      this.ws.onclose = null;

      if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close(1000, 'Client disconnect');
      }

      this.ws = null;
    }

    this.roomId = null;
    this.token = null;
    this.messageQueue = [];
    this.reconnectAttempts = 0;
  }

  /**
   * Send a message through WebSocket
   */
  sendMessage(content: string): void {
    if (!content.trim()) {
      return;
    }

    const message = JSON.stringify({
      type: 'message',
      content: content.trim(),
    });

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(message);
    } else {
      // Queue message if not connected
      console.log('WebSocket not connected, queuing message');
      this.messageQueue.push(message);

      // Attempt to reconnect if disconnected
      if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
        this.attemptReconnect();
      }
    }
  }

  /**
   * Flush queued messages
   */
  private flushMessageQueue(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN && this.messageQueue.length > 0) {
      console.log(`Flushing ${this.messageQueue.length} queued messages`);
      this.messageQueue.forEach((message) => {
        this.ws!.send(message);
      });
      this.messageQueue = [];
    }
  }

  /**
   * Register message listener
   */
  onMessage(callback: MessageCallback): () => void {
    this.messageListeners.push(callback);
    // Return unsubscribe function
    return () => {
      this.messageListeners = this.messageListeners.filter((cb) => cb !== callback);
    };
  }

  /**
   * Register connect listener
   */
  onConnect(callback: StatusCallback): () => void {
    this.connectListeners.push(callback);
    return () => {
      this.connectListeners = this.connectListeners.filter((cb) => cb !== callback);
    };
  }

  /**
   * Register disconnect listener
   */
  onDisconnect(callback: StatusCallback): () => void {
    this.disconnectListeners.push(callback);
    return () => {
      this.disconnectListeners = this.disconnectListeners.filter((cb) => cb !== callback);
    };
  }

  /**
   * Register error listener
   */
  onError(callback: ErrorCallback): () => void {
    this.errorListeners.push(callback);
    return () => {
      this.errorListeners = this.errorListeners.filter((cb) => cb !== callback);
    };
  }

  /**
   * Notify all message listeners
   */
  private notifyMessage(message: Message): void {
    this.messageListeners.forEach((callback) => {
      try {
        callback(message);
      } catch (error) {
        console.error('Error in message listener:', error);
      }
    });
  }

  /**
   * Notify status change listeners
   */
  private notifyStatusChange(status: ConnectionStatus): void {
    const listeners =
      status === 'connected'
        ? this.connectListeners
        : status === 'disconnected'
        ? this.disconnectListeners
        : [];

    listeners.forEach((callback) => {
      try {
        callback(status);
      } catch (error) {
        console.error('Error in status listener:', error);
      }
    });
  }

  /**
   * Notify all error listeners
   */
  private notifyError(error: Error): void {
    this.errorListeners.forEach((callback) => {
      try {
        callback(error);
      } catch (error) {
        console.error('Error in error listener:', error);
      }
    });
  }

  /**
   * Get current connection status
   */
  getStatus(): ConnectionStatus {
    if (!this.ws) return 'disconnected';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'disconnected';
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();
