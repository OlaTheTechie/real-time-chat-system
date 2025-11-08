import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useChat } from '../hooks/useChat';
import { ChatRoom } from '../types';
import OnlineStatusIndicator from './OnlineStatusIndicator';
import { formatTimestamp } from '../utils/helpers';

interface SidebarProps {
  onCreateChat: () => void;
  currentRoomId?: number;
}

const Sidebar: React.FC<SidebarProps> = ({ onCreateChat, currentRoomId }) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { rooms, selectRoom } = useChat();
  const [searchQuery, setSearchQuery] = useState('');

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

  // Filter rooms based on search query
  const filteredRooms = rooms.filter((room) => {
    const displayName = getRoomDisplayName(room).toLowerCase();
    const query = searchQuery.toLowerCase();
    return displayName.includes(query);
  });

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Search and Create Button */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onCreateChat}
          className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors mb-3"
        >
          + Create New Chat
        </button>

        {/* Search input */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 pl-10 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <svg
            className="absolute left-3 top-2.5 w-4 h-4 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {/* Chat Rooms List */}
      <div className="flex-1 overflow-y-auto">
        {filteredRooms.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            {searchQuery ? (
              <p className="text-sm">No chats found</p>
            ) : (
              <div>
                <svg
                  className="mx-auto h-12 w-12 text-gray-400 mb-2"
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
                <p className="text-sm">No chat rooms yet</p>
                <p className="text-xs mt-1">Create one to get started</p>
              </div>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredRooms.map((room) => (
              <div
                key={room.id}
                onClick={() => handleRoomClick(room.id)}
                className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                  currentRoomId === room.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-1">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-gray-900 truncate">
                      {getRoomDisplayName(room)}
                    </h3>
                    {room.room_type === 'one_to_one' && (
                      <OnlineStatusIndicator
                        isOnline={
                          room.members.find((m) => m.id !== user?.id)
                            ?.is_online || false
                        }
                        size="sm"
                      />
                    )}
                  </div>
                  {room.last_message && (
                    <span className="text-xs text-gray-500 flex-shrink-0 ml-2">
                      {formatTimestamp(room.last_message.timestamp)}
                    </span>
                  )}
                </div>

                {room.room_type === 'group' && (
                  <p className="text-xs text-gray-500 mb-1">
                    {getOnlineMembersCount(room)} online • {room.members.length} members
                  </p>
                )}

                {room.last_message && (
                  <p className="text-xs text-gray-600 truncate">
                    {room.last_message.sender_username}: {room.last_message.content}
                  </p>
                )}

                {room.unread_count && room.unread_count > 0 && (
                  <div className="mt-2">
                    <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold leading-none text-white bg-blue-600 rounded-full">
                      {room.unread_count > 99 ? '99+' : room.unread_count}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
