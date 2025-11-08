import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import { useAuth } from '../hooks/useAuth';
import { ChatRoom } from '../types';
import CreateChatModal from '../components/CreateChatModal';
import OnlineStatusIndicator from '../components/OnlineStatusIndicator';
import Navbar from '../components/Navbar';
import SkeletonLoader from '../components/SkeletonLoader';
import ErrorMessage from '../components/ErrorMessage';
import { formatTimestamp } from '../utils/helpers';

const ChatRoomList: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { rooms, isLoading, error, loadRooms, selectRoom } = useChat();
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadRooms();
  }, [loadRooms]);

  const handleRoomClick = async (roomId: number) => {
    await selectRoom(roomId);
    navigate(`/chat/${roomId}`);
  };





  const getRoomDisplayName = (room: ChatRoom): string => {
    if (room.room_type === 'group') {
      return room.name || 'Unnamed Group';
    } else {
      // for one-to-one, show the other user's name
      const otherMember = room.members.find((member) => member.id !== user?.id);
      return otherMember?.username || 'Unknown User';
    }
  };

  const getOnlineMembersCount = (room: ChatRoom): number => {
    return room.members.filter((member) => member.is_online).length;
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* navbar */}
      <Navbar title="Chat Rooms" />

      {/* main content - two column layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* sidebar - chat list */}
        <div className="w-full md:w-96 bg-white border-r border-gray-200 flex flex-col">
          {/* header with create button */}
          <div className="p-4 border-b border-gray-200 bg-white flex-shrink-0">
            <button
              onClick={() => setShowCreateModal(true)}
              className="w-full px-4 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all shadow-sm hover:shadow-md"
            >
              + Create New Chat
            </button>
          </div>

          {/* error message */}
          {error && (
            <div className="m-4">
              <ErrorMessage
                message={error}
                onRetry={loadRooms}
                onDismiss={() => {}}
              />
            </div>
          )}

          {/* chat list container */}
          <div className="flex-1 overflow-y-auto">
            {/* loading state */}
            {isLoading && rooms.length === 0 && (
              <SkeletonLoader type="chat-room" count={5} />
            )}

            {/* empty state */}
            {!isLoading && rooms.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full p-8 text-center">
                <svg
                  className="h-16 w-16 text-gray-300 mb-4"
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
                <h3 className="text-sm font-medium text-gray-900 mb-1">
                  No chat rooms
                </h3>
                <p className="text-sm text-gray-500">
                  Get started by creating a new chat room.
                </p>
              </div>
            )}

            {/* chat rooms list */}
            {!isLoading && rooms.length > 0 && (
              <div className="divide-y divide-gray-100">
                {rooms.map((room) => (
                  <div
                    key={room.id}
                    onClick={() => handleRoomClick(room.id)}
                    className="p-4 hover:bg-indigo-50 cursor-pointer transition-all duration-200 hover:shadow-sm animate-fade-in"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-sm font-semibold text-gray-900 truncate">
                            {getRoomDisplayName(room)}
                          </h3>
                          {room.room_type === 'one_to_one' && (
                            <OnlineStatusIndicator
                              isOnline={
                                room.members.find((m) => m.id !== user?.id)
                                  ?.is_online || false
                              }
                              lastSeen={
                                room.members.find((m) => m.id !== user?.id)
                                  ?.last_seen
                              }
                              size="sm"
                            />
                          )}
                        </div>

                        {room.room_type === 'group' && (
                          <div className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                            <svg
                              className="h-3 w-3"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                              />
                            </svg>
                            {room.members.length} members • {getOnlineMembersCount(room)} online
                          </div>
                        )}

                        {room.last_message && (
                          <p className="text-sm text-gray-600 truncate">
                            <span className="font-medium">{room.last_message.sender_username}:</span>{' '}
                            {room.last_message.content}
                          </p>
                        )}

                        {!room.last_message && (
                          <p className="text-sm text-gray-400 italic">No messages yet</p>
                        )}
                      </div>

                      <div className="ml-3 flex-shrink-0 flex flex-col items-end gap-1">
                        {room.last_message && (
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(room.last_message.timestamp)}
                          </span>
                        )}
                        {room.unread_count && room.unread_count > 0 && (
                          <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-indigo-600 rounded-full">
                            {room.unread_count > 99 ? '99+' : room.unread_count}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* main content area - placeholder */}
        <div className="hidden md:flex flex-1 items-center justify-center bg-gray-50">
          <div className="text-center text-gray-400">
            <svg
              className="mx-auto h-24 w-24 text-gray-300 mb-4"
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
            <p className="text-lg font-medium">Select a chat to start messaging</p>
          </div>
        </div>
      </div>

      {/* create chat modal */}
      <CreateChatModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
};

export default ChatRoomList;
