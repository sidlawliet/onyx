'use client';

import React from 'react';

export const ErrorBanner: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => {
  return (
    <div className="bg-error-container/30 border border-error/50 rounded p-4 text-error text-xs flex items-center justify-between my-4">
      <div className="flex items-center gap-2">
        <span className="material-symbols-outlined text-lg">warning</span>
        <span>{message}</span>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3 py-1 bg-error-container text-on-error-container rounded hover:bg-error-container/80 transition-colors text-xs font-semibold"
        >
          Retry
        </button>
      )}
    </div>
  );
};
