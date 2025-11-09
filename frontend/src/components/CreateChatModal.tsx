import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useChat } from '../hooks/useChat';
import { chatApi } from '../services/api';
import { User } from '../types';

interface CreateChatModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const CreateChatModal: React.FC<CreateChatModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const { createRoom } = useChat();

  const [roomType, setRoomType] = useState<'one_to_one' | 'group'>('one_to_one');
  const [roomName, setRoomName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [selectedUserIds, setSelectedUserIds] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);

  const loadUsers = async () => {
    setIsLoadingUsers(true);
    try {
      const users = await chatApi.getAllUsers();
      // filter out current user
      const otherUsers = users.filter((u) => u.id !== currentUser?.id);
      setAllUsers(otherUsers);
    } catch (err: any) {
      setError('Failed to load users');
      console.error('Error loading users:', err);
    } finally {
      setIsLoadingUsers(false);
    }
  };

  // load users when modal opens
  useEffect(() => {
    if (isOpen) {
      loadUsers();
    } else {
      // reset form when modal closes
      setRoomType('one_to_one');
      setRoomName('');
      setSearchQuery('');
      setSelectedUserIds([]);
      setError(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  const filteredUsers = allUsers.filter((user) =>
    user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleUserToggle = (userId: number) => {
    setSelectedUserIds((prev) => {
      if (prev.includes(userId)) {
        return prev.filter((id) => id !== userId);
      } else {
        // for one-to-one, only allow one selection
        if (roomType === 'one_to_one') {
          return [userId];
        }
        return [...prev, userId];
      }
    });
  };

  const handleCreate = async () => {
    setError(null);

    // validation
    if (selectedUserIds.length === 0) {
      setError('Please select at least one user');
      return;
    }

    if (roomType === 'group' && !roomName.trim()) {
      setError('Please enter a group name');
      return;
    }

    if (roomType === 'one_to_one' && selectedUserIds.length !== 1) {
      setError('Please select exactly one user for one-to-one chat');
      return;
    }

    setIsLoading(true);

    try {
      const newRoom = await createRoom({
        room_type: roomType,
        name: roomType === 'group' ? roomName : undefined,
        member_ids: selectedUserIds,
      });

      // navigate to the new room
      navigate(`/chat/${newRoom.id}`);
      onClose();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create chat room';
      setError(errorMessage);
      console.error('Error creating room:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">Create New Chat</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {/* room type selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chat Type
            </label>
            <div className="flex gap-4">
              <button
                onClick={() => {
                  setRoomType('one_to_one');
                  setSelectedUserIds([]);
                }}
                className={`flex-1 px-4 py-3 rounded-lg border-2 transition-colors ${
                  roomType === 'one_to_one'
                    ? 'border-blue-600 bg-blue-50 text-blue-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                <div className="font-medium">One-to-One</div>
                <div className="text-xs mt-1">Direct message with one person</div>
              </button>
              <button
                onClick={() => {
                  setRoomType('group');
                  setSelectedUserIds([]);
                }}
                className={`flex-1 px-4 py-3 rounded-lg border-2 transition-colors ${
                  roomType === 'group'
                    ? 'border-blue-600 bg-blue-50 text-blue-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                <div className="font-medium">Group Chat</div>
                <div className="text-xs mt-1">Chat with multiple people</div>
              </button>
            </div>
          </div>

          {/* group name input */}
          {roomType === 'group' && (
            <div className="mb-6">
              <label
                htmlFor="roomName"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Group Name *
              </label>
              <input
                type="text"
                id="roomName"
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
                placeholder="Enter group name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}

          {/* user search */}
          <div className="mb-4">
            <label
              htmlFor="userSearch"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Select Members *
            </label>
            <input
              type="text"
              id="userSearch"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search users by name or email..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* user list */}
          <div className="border border-gray-200 rounded-lg max-h-64 overflow-y-auto">
            {isLoadingUsers ? (
              <div className="flex justify-center items-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : filteredUsers.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No users found
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {filteredUsers.map((user) => (
                  <label
                    key={user.id}
                    className="flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedUserIds.includes(user.id)}
                      onChange={() => handleUserToggle(user.id)}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <div className="ml-3 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">
                          {user.username}
                        </span>
                        <div
                          className={`w-2 h-2 rounded-full ${
                            user.is_online ? 'bg-green-500' : 'bg-gray-400'
                          }`}
                        />
                      </div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* selected count */}
          {selectedUserIds.length > 0 && (
            <div className="mt-3 text-sm text-gray-600">
              {selectedUserIds.length} user{selectedUserIds.length !== 1 ? 's' : ''}{' '}
              selected
            </div>
          )}

          {/* error message */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={isLoading || selectedUserIds.length === 0}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Creating...' : 'Create Chat'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateChatModal;
