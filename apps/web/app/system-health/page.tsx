'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorBanner } from '@/components/common/ErrorBanner';

export default function SystemHealthPage() {
  const [health, setHealth] = useState<any | null>(null);
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [hData, aData] = await Promise.all([
        api.getSystemHealth(),
        api.getAgentsStatus(),
      ]);
      setHealth(hData);
      setAgents(aData);
    } catch (err: any) {
      setError('Failed to load system health diagnostics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex justify-between items-end pb-4 border-b border-outline-variant/50">
        <div>
          <h2 className="font-display text-2xl font-semibold text-on-surface mb-1">
            System Health & Agent Diagnostics
          </h2>
          <p className="text-sm text-on-surface-variant">
            Platform component health, active agent worker statuses, and database telemetry
          </p>
        </div>

        <button
          onClick={fetchData}
          className="px-3 py-1.5 bg-surface-container-high border border-outline-variant rounded text-xs font-semibold text-on-surface hover:bg-surface-container-highest transition-colors flex items-center gap-1.5"
        >
          <span className="material-symbols-outlined text-base">refresh</span>
          Refresh Health
        </button>
      </div>

      {error && <ErrorBanner message={error} />}

      {loading ? (
        <LoadingState message="Checking platform component diagnostics..." />
      ) : (
        <div className="flex flex-col gap-6">
          {/* Status Header Banner */}
          <div className="border border-emerald-500/40 rounded-lg bg-surface-container-lowest p-6 flex justify-between items-center">
            <div>
              <span className="text-[10px] font-mono text-on-surface-variant uppercase">Overall Status</span>
              <h3 className="text-xl font-bold text-emerald-400 mt-1 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></span>
                {health?.status || 'HEALTHY'}
              </h3>
            </div>
            <div className="text-right text-xs font-mono text-on-surface-variant">
              <div>Database: <span className="text-emerald-400 font-bold">{health?.database}</span></div>
              <div>Timestamp: <span className="text-on-surface">{new Date(health?.timestamp).toLocaleTimeString()}</span></div>
            </div>
          </div>

          {/* AI Agents Worker Grid */}
          <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6">
            <h4 className="text-xs font-mono font-semibold text-on-surface-variant uppercase mb-4">
              AI Agent Worker Statuses ({agents.length})
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((ag) => (
                <div
                  key={ag.agent_name}
                  className="p-4 bg-surface-container-low rounded border border-outline-variant/40 flex flex-col gap-2"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-xs text-on-surface">{ag.agent_name}</span>
                    <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-mono font-bold rounded">
                      {ag.status}
                    </span>
                  </div>
                  <div className="flex justify-between text-[11px] font-mono text-on-surface-variant mt-1">
                    <span>Queue: {ag.queue_depth}</span>
                    <span>Success Rate: {ag.success_rate}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
