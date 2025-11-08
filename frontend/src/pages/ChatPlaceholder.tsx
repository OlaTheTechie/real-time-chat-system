import React from 'react';
import { useAuth } from '../hooks/useAuth';

const ChatPlaceholder: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Welcome to Chat!</h1>
        <p className="mt-2 text-gray-600">
          Hello, {user?.username}! The chat interface will be implemented in the next tasks.
        </p>
        <button
          onClick={handleLogout}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default ChatPlaceholder;
