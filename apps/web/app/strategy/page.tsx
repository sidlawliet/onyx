'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorBanner } from '@/components/common/ErrorBanner';

export default function StrategyPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('');
  const [workflow, setWorkflow] = useState<any | null>(null);
  const [validationResult, setValidationResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = async () => {
    try {
      const wfList = await api.getWorkflows();
      setWorkflows(wfList);
      if (wfList.length > 0) {
        setSelectedWorkflowId(wfList[0].id);
        fetchWorkflowDetail(wfList[0].id);
      } else {
        setLoading(false);
      }
    } catch (err: any) {
      setError('Failed to fetch workflows');
      setLoading(false);
    }
  };

  const fetchWorkflowDetail = async (workflowId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getWorkflow(workflowId);
      setWorkflow(data);
    } catch (err: any) {
      setError('Failed to load workflow strategy recommendation details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const recVersion = workflow?.recommendations?.[0]?.versions?.[0];

  const handleValidate = async () => {
    if (!recVersion) return;
    setActionLoading(true);
    try {
      const res = await api.validateRecommendation(recVersion.id);
      setValidationResult(res);
    } catch (err: any) {
      alert(err.response?.data?.message || 'Mandate validation failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSubmitApproval = async () => {
    if (!recVersion) return;
    setActionLoading(true);
    try {
      await api.submitForApproval(recVersion.id);
      alert('Recommendation submitted to Human Approval Gate successfully!');
      fetchWorkflowDetail(selectedWorkflowId);
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to submit for approval');
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
            Portfolio Strategy & Mandate Validation
          </h2>
          <p className="text-sm text-on-surface-variant">
            Target asset allocations, risk metrics, and pre-trade mandate compliance checks
          </p>
        </div>

        {/* Workflow Selector */}
        {workflows.length > 0 && (
          <select
            value={selectedWorkflowId}
            onChange={(e) => {
              setSelectedWorkflowId(e.target.value);
              fetchWorkflowDetail(e.target.value);
              setValidationResult(null);
            }}
            className="bg-surface-container-low border border-outline-variant rounded px-3 py-1.5 text-xs text-on-surface focus:outline-none"
          >
            {workflows.map((wf) => (
              <option key={wf.id} value={wf.id}>
                {wf.title} ({wf.stage})
              </option>
            ))}
          </select>
        )}
      </div>

      {error && <ErrorBanner message={error} />}

      {loading ? (
        <LoadingState message="Loading portfolio strategy recommendation..." />
      ) : recVersion ? (
        <div className="flex flex-col gap-6">
          {/* Metrics Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
              <span className="text-[10px] font-mono text-on-surface-variant uppercase">Expected Return</span>
              <p className="text-xl font-bold text-emerald-400 mt-1">
                {(parseFloat(recVersion.expected_return) * 100).toFixed(1)}%
              </p>
            </div>

            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
              <span className="text-[10px] font-mono text-on-surface-variant uppercase">Annualized Volatility</span>
              <p className="text-xl font-bold text-secondary mt-1">
                {(parseFloat(recVersion.volatility) * 100).toFixed(1)}%
              </p>
            </div>

            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
              <span className="text-[10px] font-mono text-on-surface-variant uppercase">Diversification Score</span>
              <p className="text-xl font-bold text-on-surface mt-1">
                {(parseFloat(recVersion.diversification_score) * 100).toFixed(0)} / 100
              </p>
            </div>

            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
              <span className="text-[10px] font-mono text-on-surface-variant uppercase">Horizon</span>
              <p className="text-xl font-bold text-on-surface mt-1">
                {recVersion.investment_horizon_days} Days
              </p>
            </div>
          </div>

          {/* Artifact Hash & Action Bar */}
          <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <span className="text-[10px] font-mono text-on-surface-variant uppercase block">
                Deterministic SHA-256 Content Hash
              </span>
              <span className="font-mono text-xs text-secondary break-all">
                {recVersion.artifact_hash}
              </span>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleValidate}
                disabled={actionLoading}
                className="px-4 py-2 bg-surface-container-high border border-outline-variant rounded text-xs font-semibold text-on-surface hover:bg-surface-container-highest transition-colors flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-base">verified_user</span>
                Run Mandate Validation
              </button>

              <button
                onClick={handleSubmitApproval}
                disabled={actionLoading}
                className="px-4 py-2 bg-secondary-container text-on-secondary-container rounded text-xs font-semibold hover:bg-secondary-container/80 transition-colors flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-base">send</span>
                Submit to Approval Gate
              </button>
            </div>
          </div>

          {/* Validation Results Display */}
          {validationResult && (
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-xs font-mono font-semibold text-on-surface-variant uppercase">
                  Pre-Trade Mandate & Risk Rule Checks
                </h4>
                <span
                  className={`px-3 py-1 rounded text-xs font-bold font-mono ${
                    validationResult.status === 'PASS'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : 'bg-error-container text-error border border-error/40'
                  }`}
                >
                  STATUS: {validationResult.status}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {validationResult.results?.map((res: any) => (
                  <div
                    key={res.rule_code}
                    className="p-3 bg-surface-container-low rounded border border-outline-variant/40 flex items-start justify-between gap-3 text-xs"
                  >
                    <div>
                      <span className="font-bold text-on-surface block mb-1">{res.rule_code}</span>
                      <p className="text-on-surface-variant text-[11px]">{res.explanation}</p>
                    </div>
                    <span
                      className={`font-mono font-bold text-[10px] px-2 py-0.5 rounded ${
                        res.passed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-error-container text-error'
                      }`}
                    >
                      {res.passed ? 'PASS' : 'FAIL'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Target Allocations Table */}
          <div className="border border-outline-variant rounded-lg bg-surface-container-lowest overflow-hidden">
            <div className="px-6 py-4 border-b border-outline-variant bg-surface-container-low/50 text-xs font-mono font-semibold text-on-surface-variant uppercase">
              Target Asset Allocations ({recVersion.allocations?.length || 0})
            </div>

            <table className="w-full text-left text-xs">
              <thead className="bg-surface-container-high/40 text-on-surface-variant font-mono uppercase text-[10px] border-b border-outline-variant">
                <tr>
                  <th className="py-3 px-6">Symbol</th>
                  <th className="py-3 px-6">Side</th>
                  <th className="py-3 px-6">Target Weight</th>
                  <th className="py-3 px-6">Target Shares</th>
                  <th className="py-3 px-6">Trade Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30 text-on-surface">
                {recVersion.allocations?.map((alloc: any) => (
                  <tr key={alloc.id} className="hover:bg-surface-container-low/50">
                    <td className="py-3.5 px-6 font-bold">{alloc.instrument?.symbol || 'AAPL'}</td>
                    <td className="py-3.5 px-6 font-mono text-emerald-400 font-bold">{alloc.side}</td>
                    <td className="py-3.5 px-6 font-mono">{(parseFloat(alloc.target_weight) * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-6 font-mono">{parseFloat(alloc.target_quantity).toLocaleString()}</td>
                    <td className="py-3.5 px-6 text-on-surface-variant">{alloc.rationale}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-12 text-center text-xs text-on-surface-variant">
          No strategy recommendation generated yet. Go to Workflows page to generate recommendation.
        </div>
      )}
    </div>
  );
}
