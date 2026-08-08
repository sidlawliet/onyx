'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorBanner } from '@/components/common/ErrorBanner';

export default function AuditPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [traceIdFilter, setTraceIdFilter] = useState<string>('');
  const [exportPackage, setExportPackage] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = async (traceId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAuditEvents(traceId || undefined);
      setEvents(data);
    } catch (err: any) {
      setError('Failed to load audit trail events');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEvents(traceIdFilter);
  };

  const handleExport = async () => {
    setActionLoading(true);
    try {
      const exp = await api.exportAuditChain(traceIdFilter || undefined);
      setExportPackage(exp);
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to export audit chain');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex justify-between items-end pb-4 border-b border-outline-variant/50">
        <div>
          <h2 className="font-display text-2xl font-semibold text-on-surface mb-1">
            Institutional Audit Trail & Evidence Log
          </h2>
          <p className="text-sm text-on-surface-variant">
            Immutable SHA-256 hash-chained event audit log for end-to-end decision traceability
          </p>
        </div>

        <button
          onClick={handleExport}
          disabled={actionLoading}
          className="px-4 py-2 bg-secondary-container text-on-secondary-container hover:bg-secondary-container/80 rounded text-xs font-semibold transition-colors flex items-center gap-2"
        >
          <span className="material-symbols-outlined text-base">file_download</span>
          Export Audit Package
        </button>
      </div>

      {/* Filter Bar */}
      <form onSubmit={handleSearch} className="flex gap-3 items-center">
        <div className="relative flex-1 max-w-md">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">
            search
          </span>
          <input
            type="text"
            value={traceIdFilter}
            onChange={(e) => setTraceIdFilter(e.target.value)}
            placeholder="Filter by Trace ID (e.g. 11111111-1111-4111-a111-111111111111)..."
            className="w-full bg-surface-container-low border border-outline-variant rounded pl-9 pr-3 py-1.5 text-xs text-on-surface focus:outline-none focus:border-secondary font-mono"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-1.5 bg-surface-container-high border border-outline-variant text-on-surface hover:bg-surface-container-highest rounded text-xs font-semibold"
        >
          Search
        </button>
      </form>

      {error && <ErrorBanner message={error} />}

      {/* Export Package Card */}
      {exportPackage && (
        <div className="border border-emerald-500/40 rounded-lg bg-surface-container-lowest p-6 flex flex-col gap-3">
          <div className="flex justify-between items-center border-b border-outline-variant/30 pb-3">
            <h4 className="text-xs font-mono font-semibold text-emerald-400 uppercase flex items-center gap-2">
              <span className="material-symbols-outlined text-base">verified</span>
              Verified Audit Chain Export Package
            </h4>
            <span
              className={`px-3 py-0.5 rounded text-[10px] font-mono font-bold ${
                exportPackage.chain_valid ? 'bg-emerald-500/20 text-emerald-400' : 'bg-error-container text-error'
              }`}
            >
              CHAIN VALID: {exportPackage.chain_valid ? 'TRUE' : 'FALSE'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
            <div>
              <span className="text-[10px] text-on-surface-variant uppercase block">Export ID</span>
              <span className="text-on-surface">{exportPackage.export_id}</span>
            </div>
            <div>
              <span className="text-[10px] text-on-surface-variant uppercase block">Total Events</span>
              <span className="text-on-surface">{exportPackage.total_events}</span>
            </div>
            <div>
              <span className="text-[10px] text-on-surface-variant uppercase block">Manifest Hash</span>
              <span className="text-secondary break-all text-[11px]">{exportPackage.manifest_hash}</span>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <LoadingState message="Loading immutable audit trail events..." />
      ) : (
        <div className="border border-outline-variant rounded-lg bg-surface-container-lowest overflow-hidden">
          <div className="px-6 py-4 border-b border-outline-variant bg-surface-container-low/50 text-xs font-mono font-semibold text-on-surface-variant uppercase">
            Audit Event History ({events.length})
          </div>

          <table className="w-full text-left text-xs">
            <thead className="bg-surface-container-high/40 text-on-surface-variant font-mono uppercase text-[10px] border-b border-outline-variant">
              <tr>
                <th className="py-3 px-6">Timestamp</th>
                <th className="py-3 px-6">Action</th>
                <th className="py-3 px-6">Actor Type</th>
                <th className="py-3 px-6">Resource</th>
                <th className="py-3 px-6">Outcome</th>
                <th className="py-3 px-6">Event SHA-256 Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30 text-on-surface font-mono">
              {events.map((ev) => (
                <tr key={ev.id} className="hover:bg-surface-container-low/50">
                  <td className="py-3 px-6 text-on-surface-variant text-[11px]">
                    {new Date(ev.occurred_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-6 font-bold text-on-surface">{ev.action}</td>
                  <td className="py-3 px-6 text-secondary">{ev.actor_type}</td>
                  <td className="py-3 px-6 text-on-surface-variant">{ev.resource_type}</td>
                  <td className="py-3 px-6 font-bold text-emerald-400">{ev.outcome}</td>
                  <td className="py-3 px-6 text-[10px] text-on-surface-variant truncate max-w-[180px]">
                    {ev.event_hash}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
