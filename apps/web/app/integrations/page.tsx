'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorBanner } from '@/components/common/ErrorBanner';

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchIntegrations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getIntegrations();
      setIntegrations(data);
    } catch (err: any) {
      setError('Failed to load external provider integrations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntegrations();
  }, []);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex justify-between items-end pb-4 border-b border-outline-variant/50">
        <div>
          <h2 className="font-display text-2xl font-semibold text-on-surface mb-1">
            External Provider Integrations
          </h2>
          <p className="text-sm text-on-surface-variant">
            Market data, SEC EDGAR filing connectors, and FIX protocol broker execution sandboxes
          </p>
        </div>
      </div>

      {error && <ErrorBanner message={error} />}

      {loading ? (
        <LoadingState message="Loading integration providers..." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {integrations.map((int) => (
            <div
              key={int.id}
              className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6 flex flex-col justify-between gap-4"
            >
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] font-mono text-on-surface-variant uppercase">
                    Type: {int.integration_type}
                  </span>
                  <span
                    className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                      int.status === 'ACTIVE' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-surface-container-high text-on-surface-variant'
                    }`}
                  >
                    {int.status}
                  </span>
                </div>
                <h3 className="text-base font-bold text-on-surface mb-1">{int.name}</h3>
                <p className="text-xs text-on-surface-variant">Provider: {int.provider_name}</p>
              </div>

              <div className="pt-3 border-t border-outline-variant/30 flex justify-between items-center text-xs font-mono">
                <span className="text-on-surface-variant">Environment: {int.environment}</span>
                <span className="text-secondary font-semibold">Health: Normal</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
