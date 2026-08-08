'use client';

import React from 'react';

export const LoadingState: React.FC<{ message?: string }> = ({ message = 'Loading institutional data...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 gap-3">
      <div className="w-8 h-8 border-2 border-secondary border-t-transparent rounded-full animate-spin"></div>
      <p className="text-xs text-on-surface-variant font-mono">{message}</p>
    </div>
  );
};
