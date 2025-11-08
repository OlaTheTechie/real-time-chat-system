import React from 'react';
import { formatLastSeen } from '../utils/helpers';

interface OnlineStatusIndicatorProps {
  isOnline: boolean;
  lastSeen?: string;
  showLabel?: boolean;
  showLastSeen?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const OnlineStatusIndicator: React.FC<OnlineStatusIndicatorProps> = ({
  isOnline,
  lastSeen,
  showLabel = false,
  showLastSeen = false,
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  const dotClass = `${sizeClasses[size]} rounded-full ${
    isOnline ? 'bg-green-500' : 'bg-gray-400'
  }`;

  if (!showLabel && !showLastSeen) {
    return <div className={dotClass} title={isOnline ? 'Online' : 'Offline'} />;
  }

  return (
    <div className="flex items-center gap-2">
      <div className={dotClass} />
      {showLabel && (
        <span className="text-sm text-gray-600">
          {isOnline ? 'Online' : 'Offline'}
        </span>
      )}
      {showLastSeen && !isOnline && lastSeen && (
        <span className="text-xs text-gray-500">
          Last seen {formatLastSeen(lastSeen)}
        </span>
      )}
    </div>
  );
};

export default OnlineStatusIndicator;
