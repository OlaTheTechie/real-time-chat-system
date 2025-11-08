import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import { useAuth } from '../hooks/useAuth';
import { ChatRoom } from '../types';
import CreateChatModal from '../components/CreateChatModal';
import OnlineStatusIndicator from '../components/OnlineStatusIndicator';
import Navbar from '../components/Navbar';
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
      // For one-to-one, show the other user's name
      const otherMember = room.members.find((member) => member.id !== user?.id);
      return otherMember?.username || 'Unknown User';
    }
  };

  const getOnlineMembersCount = (room: ChatRoom): number => {
    return room.members.filter((member) => member.is_online).length;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <Navbar title="Chat Rooms" />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Create Chat Button */}
        <div className="mb-6">
          <button
            onClick={() => setShowCreateModal(true)}
            className="w-full sm:w-auto px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            + Create New Chat
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && rooms.length === 0 && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && rooms.length === 0 && (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No chat rooms
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating a new chat room.
            </p>
          </div>
        )}

        {/* Chat Rooms List */}
        {!isLoading && rooms.length > 0 && (
          <div className="bg-white shadow-sm rounded-lg divide-y divide-gray-200">
            {rooms.map((room) => (
              <div
                key={room.id}
                onClick={() => handleRoomClick(room.id)}
                className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-base font-semibold text-gray-900 truncate">
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
                      <p className="text-xs text-gray-500 mb-1">
                        {room.members.length} members •{' '}
                        {getOnlineMembersCount(room)} online
                      </p>
                    )}

                    {room.last_message && (
                      <p className="text-sm text-gray-600 truncate">
                        {room.last_message.sender_username}:{' '}
                        {room.last_message.content}
                      </p>
                    )}
                  </div>

                  <div className="ml-4 flex-shrink-0 flex flex-col items-end gap-1">
                    {room.last_message && (
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(room.last_message.timestamp)}
                      </span>
                    )}
                    {room.unread_count && room.unread_count > 0 && (
                      <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-blue-600 rounded-full">
                        {room.unread_count > 99 ? '99+' : room.unread_count}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Chat Modal */}
      <CreateChatModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
};

export default ChatRoomList;
