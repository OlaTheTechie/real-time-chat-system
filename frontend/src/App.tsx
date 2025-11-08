import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import Login from './pages/Login';
import Register from './pages/Register';
import PasswordReset from './pages/PasswordReset';
import ChatRoomList from './pages/ChatRoomList';
import ChatRoomView from './pages/ChatRoomView';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <AuthProvider>
        <ChatProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/password-reset" element={<PasswordReset />} />

            {/* protected routes */}
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <ChatRoomList />
                </ProtectedRoute>
              }
            />
            <Route
              path="/chat/:roomId"
              element={
                <ProtectedRoute>
                  <ChatRoomView />
                </ProtectedRoute>
              }
            />

            {/* redirect root to chat if authenticated, otherwise login */}
            <Route path="/" element={<Navigate to="/chat" replace />} />

            {/* 404 page */}
            <Route
              path="*"
              element={
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                  <div className="text-center">
                    <h1 className="text-6xl font-bold text-gray-900">404</h1>
                    <p className="mt-2 text-xl text-gray-600">Page not found</p>
                  </div>
                </div>
              }
            />
          </Routes>
        </ChatProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
