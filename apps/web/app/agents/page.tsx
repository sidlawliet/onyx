'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';

export default function AgentsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAgentsStatus().then((data) => {
      setAgents(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-end pb-4 border-b border-outline-variant/50">
        <div>
          <h2 className="font-display text-2xl font-semibold text-on-surface mb-1">
            AI Agents Workspace
          </h2>
          <p className="text-sm text-on-surface-variant">
            Sandboxed agent definitions, model versions, tool permissions, and job metrics
          </p>
        </div>
      </div>

      {loading ? (
        <LoadingState message="Loading agent workspace definitions..." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agents.map((ag) => (
            <div key={ag.agent_name} className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6 flex flex-col gap-3">
              <div className="flex justify-between items-center border-b border-outline-variant/30 pb-3">
                <h3 className="text-base font-bold text-on-surface">{ag.agent_name}</h3>
                <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-mono font-bold rounded">
                  {ag.status}
                </span>
              </div>
              <div className="text-xs text-on-surface-variant flex justify-between font-mono">
                <span>Model: Claude 3.5 Sonnet</span>
                <span>Success Rate: {ag.success_rate}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
