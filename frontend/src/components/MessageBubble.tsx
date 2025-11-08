import React from 'react';
import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
  isOwnMessage: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isOwnMessage }) => {
  // format timestamp to readable format
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
    <div className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} group animate-fade-in`}>
      <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isOwnMessage ? 'order-2' : 'order-1'}`}>
        {/* sender username (only show for other users' messages) */}
        {!isOwnMessage && message.sender_username && (
          <div className="text-xs font-medium text-gray-600 mb-1 px-2">
            {message.sender_username}
          </div>
        )}
        
        {/* message bubble */}
        <div
          className={`rounded-2xl px-4 py-2.5 break-words shadow-sm transition-all duration-200 group-hover:shadow-md ${
            isOwnMessage
              ? 'bg-indigo-600 text-white rounded-br-md'
              : 'bg-white text-gray-900 rounded-bl-md border border-gray-200'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
          
          {/* message metadata */}
          <div
            className={`flex items-center gap-2 mt-1.5 text-xs ${
              isOwnMessage ? 'text-indigo-100' : 'text-gray-500'
            }`}
          >
            <span>{formatTime(message.timestamp)}</span>
            {message.is_edited && (
              <span className="flex items-center gap-0.5">
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                edited
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
