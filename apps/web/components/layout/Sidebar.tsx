'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  const navItems = [
    { name: 'Workflows', href: '/workflow', icon: 'account_tree' },
    { name: 'Intelligence', href: '/intelligence', icon: 'psychology' },
    { name: 'Strategy', href: '/strategy', icon: 'insights' },
    { name: 'Approvals', href: '/approvals', icon: 'fact_check' },
    { name: 'Execution', href: '/execution', icon: 'play_circle' },
    { name: 'Monitoring', href: '/monitoring', icon: 'monitor_heart' },
    { name: 'Audit Trail', href: '/audit', icon: 'history' },
  ];

  const systemItems = [
    { name: 'AI Agents', href: '/agents', icon: 'smart_toy' },
    { name: 'Integrations', href: '/integrations', icon: 'extension' },
    { name: 'System Health', href: '/system-health', icon: 'health_and_safety' },
  ];

  return (
    <nav className="w-[240px] h-screen fixed left-0 top-0 bg-surface-container-lowest border-r border-outline-variant flex flex-col justify-between py-6 z-50 select-none">
      <div>
        <div className="px-6 mb-8">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-primary-container border border-outline-variant flex items-center justify-center text-secondary font-bold text-xs tracking-tighter">
              OX
            </div>
            <div>
              <h1 className="font-display text-headline-sm font-semibold text-on-surface text-lg leading-tight">
                Onyx Operations
              </h1>
              <p className="font-mono-label text-[11px] text-on-surface-variant uppercase tracking-wider">
                Institutional Grade
              </p>
            </div>
          </div>
        </div>

        <ul className="flex flex-col gap-1">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`h-10 flex items-center pl-4 pr-4 transition-colors cursor-pointer text-sm font-medium ${
                    isActive
                      ? 'text-secondary font-bold border-l-2 border-secondary bg-surface-container-low'
                      : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
                  }`}
                >
                  <span
                    className="material-symbols-outlined mr-3 text-lg"
                    style={isActive ? { fontVariationSettings: "'FILL' 1" } : {}}
                  >
                    {item.icon}
                  </span>
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      <div>
        <div className="px-6 py-2 border-t border-outline-variant/30">
          <p className="font-mono-label text-[11px] text-on-surface-variant uppercase tracking-wider mb-2">
            SYSTEM
          </p>
        </div>
        <ul className="flex flex-col gap-1">
          {systemItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`h-9 flex items-center pl-4 pr-4 transition-colors cursor-pointer text-sm font-medium ${
                    isActive
                      ? 'text-secondary font-bold border-l-2 border-secondary bg-surface-container-low'
                      : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
                  }`}
                >
                  <span className="material-symbols-outlined mr-3 text-lg">{item.icon}</span>
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
};
