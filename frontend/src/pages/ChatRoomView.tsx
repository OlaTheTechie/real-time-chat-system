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
import { Message } from '../types';

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

  // Get access token for WebSocket
  const token = localStorage.getItem('access_token');

  // WebSocket connection
  const {
    sendMessage: sendWebSocketMessage,
    connectionStatus,
    isConnected,
  } = useWebSocket({
    roomId: currentRoom?.id || null,
    token: token,
    onMessage: (message: Message) => {
      // Add incoming WebSocket message to chat context
      addMessage(message);
    },
    onError: (error: Error) => {
      console.error('WebSocket error:', error);
      setWsError(error.message);
      // Fall back to REST API after WebSocket error
      setUseRestFallback(true);
    },
  });

  // Load room when component mounts or roomId changes
  useEffect(() => {
    if (roomId) {
      const id = parseInt(roomId, 10);
      if (!isNaN(id)) {
        selectRoom(id);
        setCurrentPage(1);
      }
    }
  }, [roomId, selectRoom]);

  // Auto-scroll to latest message when new messages arrive
  useEffect(() => {
    if (messages.length > 0 && !isLoadingMore) {
      scrollToBottom();
    }
  }, [messages, isLoadingMore]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (content: string) => {
    // Use WebSocket if connected, otherwise fall back to REST API
    if (isConnected && !useRestFallback) {
      sendWebSocketMessage(content);
    } else {
      await sendMessage(content);
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

      // Maintain scroll position after loading more messages
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

  // Get room display name
  const getRoomName = () => {
    if (!currentRoom) return '';
    
    if (currentRoom.room_type === 'group') {
      return currentRoom.name || 'Group Chat';
    }
    
    // For one-to-one, show the other user's name
    const otherMember = currentRoom.members.find(m => m.id !== user?.id);
    return otherMember?.username || 'Chat';
  };

  // Get online members count
  const getOnlineMembersCount = () => {
    if (!currentRoom) return 0;
    return currentRoom.members.filter(m => m.is_online).length;
  };

  if (isLoading && !currentRoom) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading chat room...</p>
        </div>
      </div>
    );
  }

  if (error && !currentRoom) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={handleBackToList}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Back to Chat List
          </button>
        </div>
      </div>
    );
  }

  if (!currentRoom) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Room not found</p>
          <button
            onClick={handleBackToList}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Back to Chat List
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Navbar */}
      <Navbar
        showBackButton={!showSidebar}
        onBackClick={handleBackToList}
        title={getRoomName()}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar - hidden on mobile by default, shown on desktop */}
        {showSidebar && (
          <div className="hidden md:block">
            <Sidebar
              onCreateChat={() => setShowCreateModal(true)}
              currentRoomId={currentRoom?.id}
            />
          </div>
        )}

        {/* Main chat area */}
        <div className="flex-1 flex flex-col">
          {/* Room info bar */}
          <div className="bg-white border-b border-gray-200 px-4 py-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {/* Connection status indicator */}
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

          {/* Member list dropdown */}
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

          {/* Messages container */}
          <div
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto px-4 py-4"
          >
        {/* Load more button */}
        {messages.length > 0 && hasMoreMessages && (
          <div className="text-center mb-4">
            <button
              onClick={handleLoadMore}
              disabled={isLoadingMore}
              className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              {isLoadingMore ? 'Loading...' : 'Load More Messages'}
            </button>
          </div>
        )}

        {/* Empty state */}
        {messages.length === 0 && !isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <svg
                className="w-16 h-16 mx-auto mb-4 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <p className="text-lg">No messages yet</p>
              <p className="text-sm mt-1">Start the conversation!</p>
            </div>
          </div>
        )}

        {/* Messages list */}
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isOwnMessage={message.sender_id === user?.id}
          />
        ))}

            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>

          {/* Message input */}
          <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />

          {/* Error toast */}
          {error && (
            <div className="fixed bottom-20 left-1/2 transform -translate-x-1/2 bg-red-500 text-white px-4 py-2 rounded-md shadow-lg">
              {error}
            </div>
          )}
          
          {/* WebSocket error toast */}
          {wsError && (
            <div className="fixed bottom-32 left-1/2 transform -translate-x-1/2 bg-orange-500 text-white px-4 py-2 rounded-md shadow-lg">
              WebSocket: {wsError} (Using REST fallback)
            </div>
          )}
        </div>
      </div>

      {/* Create Chat Modal */}
      <CreateChatModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
};

export default ChatRoomView;
