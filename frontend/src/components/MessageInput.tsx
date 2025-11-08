import React, { useState, KeyboardEvent, ChangeEvent } from 'react';

interface MessageInputProps {
  onSendMessage: (content: string) => Promise<void>;
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  const MAX_LENGTH = 2000;

  const handleSend = async () => {
    const trimmedMessage = message.trim();
    
    // prevent sending empty messages
    if (!trimmedMessage || isSending || disabled) {
      return;
    }

    setIsSending(true);
    try {
      await onSendMessage(trimmedMessage);
      // clear input after successful send
      setMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
      // keep the message in the input on error
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // enter key to send (shift+enter for new line)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    // enforce character limit
    if (value.length <= MAX_LENGTH) {
      setMessage(value);
    }
  };

  const remainingChars = MAX_LENGTH - message.length;
  const showCharLimit = message.length > MAX_LENGTH * 0.8;

  return (
    <div className="border-t border-gray-200 bg-white p-4 shadow-lg">
      <div className="flex items-end gap-3">
        {/* text input field */}
        <div className="flex-1">
          <textarea
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            disabled={disabled || isSending}
            rows={1}
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none disabled:bg-gray-100 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
            style={{
              minHeight: '48px',
              maxHeight: '120px',
              overflowY: 'auto',
            }}
          />
          
          {/* character limit indicator */}
          {showCharLimit && (
            <div
              className={`text-xs mt-1.5 px-1 ${
                remainingChars < 100 ? 'text-red-500 font-medium' : 'text-gray-500'
              }`}
            >
              {remainingChars} characters remaining
            </div>
          )}
        </div>

        {/* send button */}
        <button
          onClick={handleSend}
          disabled={!message.trim() || disabled || isSending}
          className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md disabled:shadow-none"
          style={{ minHeight: '48px' }}
        >
          {isSending ? (
            <span className="flex items-center gap-2">
              <svg
                className="animate-spin h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </span>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default MessageInput;
