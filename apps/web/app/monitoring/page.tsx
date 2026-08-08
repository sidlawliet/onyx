'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorBanner } from '@/components/common/ErrorBanner';

export default function MonitoringPage() {
  const [portfolios, setPortfolios] = useState<any[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>('');
  const [holdings, setHoldings] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const portList = await api.getPortfolios();
      setPortfolios(portList);
      if (portList.length > 0) {
        setSelectedPortfolioId(portList[0].id);
        await loadPortfolioData(portList[0].id);
      } else {
        setLoading(false);
      }
    } catch (err: any) {
      setError('Failed to load portfolio monitoring data');
      setLoading(false);
    }
  };

  const loadPortfolioData = async (portfolioId: string) => {
    setLoading(true);
    try {
      const [holdData, alertData] = await Promise.all([
        api.getHoldings(portfolioId),
        api.getAlerts(portfolioId),
      ]);
      setHoldings(holdData);
      setAlerts(alertData);
    } catch (err: any) {
      setError('Failed to fetch holdings or drift alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCaptureSnapshots = async () => {
    if (!selectedPortfolioId) return;
    setActionLoading(true);
    try {
      await api.captureSnapshots(selectedPortfolioId);
      await loadPortfolioData(selectedPortfolioId);
      alert('Portfolio holding snapshots captured and drift alerts evaluated successfully!');
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to capture holding snapshots');
    } finally {
      setActionLoading(false);
    }
  };

  const selectedPortfolio = portfolios.find((p) => p.id === selectedPortfolioId);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex justify-between items-end pb-4 border-b border-outline-variant/50">
        <div>
          <h2 className="font-display text-2xl font-semibold text-on-surface mb-1">
            Portfolio Monitoring & Drift Analytics
          </h2>
          <p className="text-sm text-on-surface-variant">
            Real-time holding snapshots, target allocation drift monitoring, and automated alerts
          </p>
        </div>

        {/* Portfolio Selector */}
        {portfolios.length > 0 && (
          <select
            value={selectedPortfolioId}
            onChange={(e) => {
              setSelectedPortfolioId(e.target.value);
              loadPortfolioData(e.target.value);
            }}
            className="bg-surface-container-low border border-outline-variant rounded px-3 py-1.5 text-xs text-on-surface focus:outline-none"
          >
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.code})
              </option>
            ))}
          </select>
        )}
      </div>

      {error && <ErrorBanner message={error} />}

      {loading ? (
        <LoadingState message="Loading position holdings and portfolio drift alerts..." />
      ) : (
        <div className="flex flex-col gap-6">
          {/* Portfolio Summary Card */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
              <span className="text-[10px] font-mono text-on-surface-variant uppercase">Fund Name</span>
              <p className="text-base font-bold text-on-surface mt-1">
                {selectedPortfolio?.name || 'GROWTH-01'}
              </p>
            </div>

            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
              <span className="text-[10px] font-mono text-on-surface-variant uppercase">Base Currency</span>
              <p className="text-base font-bold text-secondary mt-1">
                {selectedPortfolio?.base_currency || 'USD'}
              </p>
            </div>

            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
              <span className="text-[10px] font-mono text-on-surface-variant uppercase">Drift Alerts</span>
              <p className="text-base font-bold text-amber-400 mt-1">
                {alerts.length} Active
              </p>
            </div>

            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4 flex items-center justify-end">
              <button
                onClick={handleCaptureSnapshots}
                disabled={actionLoading}
                className="px-4 py-2 bg-secondary-container text-on-secondary-container rounded text-xs font-semibold hover:bg-secondary-container/80 transition-colors flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-base">camera_alt</span>
                Capture Snapshots
              </button>
            </div>
          </div>

          {/* Active Drift Alerts */}
          {alerts.length > 0 && (
            <div className="border border-amber-500/40 rounded-lg bg-surface-container-lowest p-6">
              <h4 className="text-xs font-mono font-semibold text-amber-400 uppercase mb-3 flex items-center gap-2">
                <span className="material-symbols-outlined text-base">warning</span>
                Active Portfolio Drift Alerts ({alerts.length})
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {alerts.map((alt) => (
                  <div
                    key={alt.id}
                    className="p-3 bg-surface-container-low rounded border border-outline-variant/40 flex flex-col gap-1 text-xs"
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-on-surface">{alt.title}</span>
                      <span className="px-2 py-0.5 bg-amber-500/20 text-amber-400 text-[10px] font-bold rounded">
                        {alt.severity}
                      </span>
                    </div>
                    <p className="text-on-surface-variant text-[11px]">{alt.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Holding Snapshots Table */}
          <div className="border border-outline-variant rounded-lg bg-surface-container-lowest overflow-hidden">
            <div className="px-6 py-4 border-b border-outline-variant bg-surface-container-low/50 text-xs font-mono font-semibold text-on-surface-variant uppercase">
              Current Position Holdings ({holdings.length})
            </div>

            <table className="w-full text-left text-xs">
              <thead className="bg-surface-container-high/40 text-on-surface-variant font-mono uppercase text-[10px] border-b border-outline-variant">
                <tr>
                  <th className="py-3 px-6">Instrument</th>
                  <th className="py-3 px-6">Quantity</th>
                  <th className="py-3 px-6">Market Price</th>
                  <th className="py-3 px-6">Market Value</th>
                  <th className="py-3 px-6">Current Weight</th>
                  <th className="py-3 px-6">Target Weight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30 text-on-surface font-mono">
                {holdings.map((h) => (
                  <tr key={h.id} className="hover:bg-surface-container-low/50">
                    <td className="py-3.5 px-6 font-bold text-secondary">{h.instrument?.symbol || 'AAPL'}</td>
                    <td className="py-3.5 px-6">{parseFloat(h.quantity).toLocaleString()}</td>
                    <td className="py-3.5 px-6">${parseFloat(h.market_price).toFixed(2)}</td>
                    <td className="py-3.5 px-6">${parseFloat(h.market_value).toLocaleString()}</td>
                    <td className="py-3.5 px-6 font-bold text-emerald-400">
                      {(parseFloat(h.weight) * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-6 text-on-surface-variant">
                      {(parseFloat(h.target_weight) * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
