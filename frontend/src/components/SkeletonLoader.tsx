import React from 'react';

interface SkeletonLoaderProps {
  type: 'chat-room' | 'message' | 'text';
  count?: number;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ type, count = 1 }) => {
  const renderChatRoomSkeleton = () => (
    <div className="p-4 border-b border-gray-100 animate-pulse">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
        <div className="h-3 bg-gray-200 rounded w-12"></div>
      </div>
    </div>
  );

  const renderMessageSkeleton = () => (
    <div className="flex justify-start mb-4 animate-pulse">
      <div className="max-w-xs lg:max-w-md">
        <div className="h-3 bg-gray-200 rounded w-20 mb-2"></div>
        <div className="bg-gray-200 rounded-2xl rounded-bl-md p-4">
          <div className="h-3 bg-gray-300 rounded w-48 mb-2"></div>
          <div className="h-3 bg-gray-300 rounded w-32"></div>
        </div>
      </div>
    </div>
  );

  const renderTextSkeleton = () => (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
  );

  const renderSkeleton = () => {
    switch (type) {
      case 'chat-room':
        return renderChatRoomSkeleton();
      case 'message':
        return renderMessageSkeleton();
      case 'text':
        return renderTextSkeleton();
      default:
        return null;
    }
  };

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index}>{renderSkeleton()}</div>
      ))}
    </>
  );
};

export default SkeletonLoader;
