import React from 'react';
import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
  isOwnMessage: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isOwnMessage }) => {
  // Format timestamp to readable format
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isOwnMessage ? 'order-2' : 'order-1'}`}>
        {/* Sender username (only show for other users' messages) */}
        {!isOwnMessage && message.sender_username && (
          <div className="text-xs text-gray-600 mb-1 px-1">
            {message.sender_username}
          </div>
        )}
        
        {/* Message bubble */}
        <div
          className={`rounded-lg px-4 py-2 break-words ${
            isOwnMessage
              ? 'bg-indigo-600 text-white rounded-br-none'
              : 'bg-gray-200 text-gray-900 rounded-bl-none'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          
          {/* Message metadata */}
          <div
            className={`flex items-center gap-2 mt-1 text-xs ${
              isOwnMessage ? 'text-indigo-100' : 'text-gray-500'
            }`}
          >
            <span>{formatTime(message.timestamp)}</span>
            {message.is_edited && <span>(edited)</span>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
