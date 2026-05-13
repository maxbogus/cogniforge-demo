'use client';

import React from 'react';
import { Loader2, CheckCircle2, AlertCircle, Clock, XCircle } from 'lucide-react';

export type StatusType = 'pending' | 'processing' | 'completed' | 'error';

interface StatusConfig {
  label: string;
  color: string;
  bgColor: string;
  icon: React.ReactNode;
}

const statusConfig: Record<StatusType, StatusConfig> = {
  pending: {
    label: 'Ожидает',
    color: 'text-navy-600',
    bgColor: 'bg-navy-100 border-navy-200',
    icon: <Clock className="w-3.5 h-3.5" />,
  },
  processing: {
    label: 'Обрабатывается',
    color: 'text-sea-600',
    bgColor: 'bg-sea-100 border-sea-200',
    icon: <Loader2 className="w-3.5 h-3.5 animate-spin" />,
  },
  completed: {
    label: 'Завершено',
    color: 'text-green-600',
    bgColor: 'bg-green-100 border-green-200',
    icon: <CheckCircle2 className="w-3.5 h-3.5" />,
  },
  error: {
    label: 'Ошибка',
    color: 'text-red-600',
    bgColor: 'bg-red-100 border-red-200',
    icon: <XCircle className="w-3.5 h-3.5" />,
  },
};

interface StatusBadgeProps {
  status: StatusType;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  showIcon = true,
  className = '',
}) => {
  const config = statusConfig[status];

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-2.5 py-1 text-sm gap-1.5',
    lg: 'px-3 py-1.5 text-base gap-2',
  };

  return (
    <span
      className={`
        inline-flex items-center font-medium rounded-full border
        ${config.color}
        ${config.bgColor}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {showIcon && <span className="flex-shrink-0">{config.icon}</span>}
      <span>{config.label}</span>
    </span>
  );
};

// Extended badge with progress indicator
interface StatusBadgeWithProgressProps extends StatusBadgeProps {
  progress?: number;
}

export const StatusBadgeWithProgress: React.FC<StatusBadgeWithProgressProps> = ({
  status,
  progress,
  size = 'md',
  showIcon = true,
  className = '',
}) => {
  const config = statusConfig[status];

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  };

  return (
    <div
      className={`
        inline-flex items-center gap-2 font-medium rounded-full border px-3 py-1
        ${config.color}
        ${config.bgColor}
        ${className}
      `}
    >
      {showIcon && (
        <span className={`flex-shrink-0 ${iconSizes[size]}`}>
          {status === 'processing' ? (
            <Loader2 className={`${iconSizes[size]} animate-spin`} />
          ) : status === 'completed' ? (
            <CheckCircle2 className={iconSizes[size]} />
          ) : status === 'error' ? (
            <AlertCircle className={iconSizes[size]} />
          ) : (
            <Clock className={iconSizes[size]} />
          )}
        </span>
      )}
      <span>{config.label}</span>
      {progress !== undefined && (
        <span className="ml-1 font-normal opacity-75">({progress}%)</span>
      )}
    </div>
  );
};

export default StatusBadge;
