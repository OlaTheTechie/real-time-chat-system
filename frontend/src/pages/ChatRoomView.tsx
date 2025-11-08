import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useChat } from '../hooks/useChat';
import { useWebSocket } from '../hooks/useWebSocket';
import MessageBubble from '../components/MessageBubble';
import MessageInput from '../components/MessageInput';
import OnlineStatusIndicator from '../components/OnlineStatusIndicator';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import CreateChatModal from '../components/CreateChatModal';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Toast from '../components/Toast';
import { Message } from '../types';
import { useToast } from '../hooks/useToast';

const ChatRoomView: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { currentRoom, messages, isLoading, error, hasMoreMessages, selectRoom, sendMessage, loadMessages, addMessage } = useChat();
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);
  const [useRestFallback, setUseRestFallback] = useState(false);
  const [showMemberList, setShowMemberList] = useState(false);
  const [showSidebar] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const { toasts, hideToast } = useToast();

  // get access token for websocket
  const token = localStorage.getItem('access_token');

  // websocket connection
  const {
    sendMessage: sendWebSocketMessage,
    connectionStatus,
    isConnected,
  } = useWebSocket({
    roomId: currentRoom?.id || null,
    token: token,
    onMessage: (message: Message) => {
      // add incoming websocket message to chat context
      addMessage(message);
    },
    onError: (error: Error) => {
      console.error('WebSocket error:', error);
      setWsError(error.message);
      // fall back to rest api after websocket error
      setUseRestFallback(true);
    },
  });

  // load room when component mounts or roomid changes
  useEffect(() => {
    if (roomId) {
      const id = parseInt(roomId, 10);
      if (!isNaN(id)) {
        selectRoom(id);
        setCurrentPage(1);
      }
    }
  }, [roomId, selectRoom]);

  // auto-scroll to latest message when new messages arrive
  useEffect(() => {
    if (messages.length > 0 && !isLoadingMore) {
      scrollToBottom();
    }
  }, [messages, isLoadingMore]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (content: string) => {
    console.log('Sending message:', { content, isConnected, useRestFallback, currentRoom: currentRoom?.id });
    
    try {
      // use websocket if connected, otherwise fall back to rest api
      if (isConnected && !useRestFallback) {
        console.log('Using WebSocket to send message');
        sendWebSocketMessage(content);
      } else {
        console.log('Using REST API to send message');
        await sendMessage(content);
      }
      console.log('Message sent successfully');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleLoadMore = async () => {
    if (!currentRoom || isLoadingMore || !hasMoreMessages) return;

    setIsLoadingMore(true);
    const previousScrollHeight = messagesContainerRef.current?.scrollHeight || 0;

    try {
      const nextPage = currentPage + 1;
      await loadMessages(currentRoom.id, nextPage);
      setCurrentPage(nextPage);

      // maintain scroll position after loading more messages
      setTimeout(() => {
        if (messagesContainerRef.current) {
          const newScrollHeight = messagesContainerRef.current.scrollHeight;
          messagesContainerRef.current.scrollTop = newScrollHeight - previousScrollHeight;
        }
      }, 0);
    } catch (err) {
      console.error('Failed to load more messages:', err);
    } finally {
      setIsLoadingMore(false);
    }
  };

  const handleBackToList = () => {
    navigate('/chat');
  };

  // get room display name
  const getRoomName = () => {
    if (!currentRoom) return '';
    
    if (currentRoom.room_type === 'group') {
      return currentRoom.name || 'Group Chat';
    }
    
    // for one-to-one, show the other user's name
    const otherMember = currentRoom.members.find(m => m.id !== user?.id);
    return otherMember?.username || 'Chat';
  };

  // get online members count
  const getOnlineMembersCount = () => {
    if (!currentRoom) return 0;
    return currentRoom.members.filter(m => m.is_online).length;
  };

  if (isLoading && !currentRoom) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner size="lg" text="Loading chat room..." />
      </div>
    );
  }

  if (error && !currentRoom) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="max-w-md w-full">
          <ErrorMessage
            message={error}
            onRetry={() => roomId && selectRoom(parseInt(roomId, 10))}
          />
          <button
            onClick={handleBackToList}
            className="mt-4 w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Back to Chat List
          </button>
        </div>
      </div>
    );
  }

  if (!currentRoom) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="text-center">
          <svg
            className="mx-auto h-16 w-16 text-gray-300 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <p className="text-gray-600 mb-4 text-lg">Room not found</p>
          <button
            onClick={handleBackToList}
            className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all shadow-sm hover:shadow-md"
          >
            Back to Chat List
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* navbar */}
      <Navbar
        showBackButton={!showSidebar}
        onBackClick={handleBackToList}
        title={getRoomName()}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* sidebar - hidden on mobile by default, shown on desktop */}
        {showSidebar && (
          <div className="hidden md:block">
            <Sidebar
              onCreateChat={() => setShowCreateModal(true)}
              currentRoomId={currentRoom?.id}
            />
          </div>
        )}

        {/* main chat area */}
        <div className="flex-1 flex flex-col">
          {/* room info bar */}
          <div className="bg-white border-b border-gray-200 px-4 py-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {/* connection status indicator */}
                {connectionStatus === 'connected' && (
                  <span className="flex items-center gap-1 text-xs text-green-600">
                    <span className="w-2 h-2 bg-green-600 rounded-full"></span>
                    Live
                  </span>
                )}
                {connectionStatus === 'connecting' && (
                  <span className="flex items-center gap-1 text-xs text-yellow-600">
                    <span className="w-2 h-2 bg-yellow-600 rounded-full animate-pulse"></span>
                    Connecting...
                  </span>
                )}
                {connectionStatus === 'disconnected' && !useRestFallback && (
                  <span className="flex items-center gap-1 text-xs text-gray-500">
                    <span className="w-2 h-2 bg-gray-500 rounded-full"></span>
                    Offline
                  </span>
                )}
                {(connectionStatus === 'error' || useRestFallback) && (
                  <span className="flex items-center gap-1 text-xs text-orange-600">
                    <span className="w-2 h-2 bg-orange-600 rounded-full"></span>
                    REST Mode
                  </span>
                )}
              </div>

              <button
                onClick={() => setShowMemberList(!showMemberList)}
                className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
              >
                {getOnlineMembersCount()} online • {currentRoom.members.length} members
                <svg
                  className={`w-4 h-4 transition-transform ${showMemberList ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>

          {/* member list dropdown */}
          {showMemberList && currentRoom && (
            <div className="bg-white border-b border-gray-200 px-4 py-3">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Members</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {currentRoom.members.map((member) => (
                  <div key={member.id} className="flex items-center justify-between py-1">
                    <div className="flex items-center gap-2">
                      <OnlineStatusIndicator
                        isOnline={member.is_online}
                        lastSeen={member.last_seen}
                        size="sm"
                      />
                      <span className="text-sm text-gray-900">
                        {member.username}
                        {member.id === user?.id && (
                          <span className="text-gray-500 ml-1">(You)</span>
                        )}
                      </span>
                    </div>
                    {!member.is_online && (
                      <OnlineStatusIndicator
                        isOnline={false}
                        lastSeen={member.last_seen}
                        showLastSeen={true}
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* messages container */}
          <div
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto px-4 py-4 bg-gradient-to-b from-gray-50 to-white"
          >
        {/* load more button */}
        {messages.length > 0 && hasMoreMessages && (
          <div className="text-center mb-4 animate-fade-in">
            <button
              onClick={handleLoadMore}
              disabled={isLoadingMore}
              className="px-4 py-2 text-sm bg-white text-gray-700 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed shadow-sm border border-gray-200 transition-all hover:shadow-md"
            >
              {isLoadingMore ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Loading...
                </span>
              ) : (
                'Load More Messages'
              )}
            </button>
          </div>
        )}

        {/* empty state */}
        {messages.length === 0 && !isLoading && (
          <div className="flex items-center justify-center h-full animate-fade-in">
            <div className="text-center text-gray-400">
              <svg
                className="w-20 h-20 mx-auto mb-4 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <p className="text-lg font-medium text-gray-500">No messages yet</p>
              <p className="text-sm mt-1">Start the conversation!</p>
            </div>
          </div>
        )}

        {/* messages list */}
        <div className="space-y-2">
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              isOwnMessage={message.sender_id === user?.id}
            />
          ))}
        </div>

            {/* scroll anchor */}
            <div ref={messagesEndRef} />
          </div>

          {/* message input */}
          <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />

        </div>
      </div>

      {/* toast notifications */}
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => hideToast(toast.id)}
        />
      ))}

      {/* error toast */}
      {error && (
        <Toast
          message={error}
          type="error"
          onClose={() => {}}
          duration={5000}
        />
      )}
      
      {/* websocket error toast */}
      {wsError && (
        <Toast
          message={`WebSocket: ${wsError} (Using REST fallback)`}
          type="warning"
          onClose={() => setWsError(null)}
          duration={5000}
        />
      )}

      {/* create chat modal */}
      <CreateChatModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
};

export default ChatRoomView;
