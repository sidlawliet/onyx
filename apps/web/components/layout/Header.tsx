'use client';

import React from 'react';
import { useAuth } from '@/lib/auth-context';

interface HeaderProps {
  title?: string;
}

export const Header: React.FC<HeaderProps> = ({ title = 'Operations Control Plane' }) => {
  const { user, logout } = useAuth();

  return (
    <header className="h-14 border-b border-outline-variant bg-surface-container-lowest flex items-center justify-between px-6 sticky top-0 z-40">
      <div className="flex items-center gap-4">
        <h2 className="text-base font-semibold text-on-surface">{title}</h2>
        <span className="bg-surface-container-highest text-on-surface-variant text-[11px] font-mono px-2 py-0.5 rounded border border-outline-variant/40">
          Tenant: {user?.tenant_name || 'InvestOps Institutional Demo'}
        </span>
      </div>

      <div className="flex items-center gap-5">
        <div className="flex items-center gap-2 text-xs text-on-surface-variant">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>System Healthy</span>
        </div>

        <div className="h-4 w-px bg-outline-variant/40"></div>

        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end">
            <span className="text-xs font-semibold text-on-surface">
              {user?.full_name || 'Portfolio Approver'}
            </span>
            <span className="text-[10px] text-on-surface-variant uppercase font-mono">
              {user?.roles?.[0] || 'APPROVER'}
            </span>
          </div>

          <div className="w-8 h-8 rounded bg-surface-container-high border border-outline-variant flex items-center justify-center text-xs font-bold text-secondary">
            {user?.full_name ? user.full_name.substring(0, 2).toUpperCase() : 'PA'}
          </div>

          <button
            onClick={logout}
            className="text-on-surface-variant hover:text-error transition-colors p-1"
            title="Sign out"
          >
            <span className="material-symbols-outlined text-lg">logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};
