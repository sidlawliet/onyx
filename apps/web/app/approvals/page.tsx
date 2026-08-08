'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorBanner } from '@/components/common/ErrorBanner';

export default function ApprovalsPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('');
  const [workflow, setWorkflow] = useState<any | null>(null);
  const [attestation, setAttestation] = useState(
    'I attest that I have reviewed the SEC Form 10-K research report and mandate validation results and approve this allocation.'
  );
  const [mfaVerified, setMfaVerified] = useState(true);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [decisionSuccess, setDecisionSuccess] = useState<string | null>(null);

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
      setError('Failed to load decision workspace details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const task = workflow?.approval_tasks?.[0];
  const manifest = task?.artifact_manifest;
  const recVersion = manifest?.recommendation_version || workflow?.recommendations?.[0]?.versions?.[0];

  const handleDecision = async (decision: 'APPROVE' | 'REJECT') => {
    if (!task || !recVersion) return;
    setActionLoading(true);
    setError(null);
    try {
      const res = await api.submitApprovalDecision(
        task.id,
        decision,
        attestation,
        recVersion.artifact_hash
      );
      setDecisionSuccess(`Decision ${decision} submitted successfully! Decision ID: ${res.id}`);
      fetchWorkflowDetail(selectedWorkflowId);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to submit approval decision');
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
            Human Decision Workspace
          </h2>
          <p className="text-sm text-on-surface-variant">
            Human Investment Authority Gate — Sign-off required prior to trade release
          </p>
        </div>

        {/* Workflow Selector */}
        {workflows.length > 0 && (
          <select
            value={selectedWorkflowId}
            onChange={(e) => {
              setSelectedWorkflowId(e.target.value);
              fetchWorkflowDetail(e.target.value);
              setDecisionSuccess(null);
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
      {decisionSuccess && (
        <div className="p-4 bg-emerald-500/20 border border-emerald-500/40 rounded text-emerald-400 text-xs font-semibold">
          {decisionSuccess}
        </div>
      )}

      {loading ? (
        <LoadingState message="Loading approval task and locked artifact manifest..." />
      ) : recVersion ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Review Column */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {/* Locked Manifest Banner */}
            <div className="border border-secondary/40 rounded-lg bg-surface-container-lowest p-6 flex flex-col gap-3">
              <div className="flex justify-between items-center border-b border-outline-variant/30 pb-3">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-xl">lock</span>
                  <span className="text-sm font-bold text-on-surface">LOCKED ARTIFACT MANIFEST</span>
                </div>
                <span className="px-2.5 py-1 bg-secondary-container text-on-secondary-container text-[11px] font-mono font-bold rounded">
                  Schema: v1.0.0
                </span>
              </div>

              <div>
                <span className="text-[10px] font-mono text-on-surface-variant uppercase">
                  Locked SHA-256 Artifact Hash
                </span>
                <p className="font-mono text-xs text-secondary break-all mt-1 bg-surface-container-low p-2 rounded border border-outline-variant/30">
                  {recVersion.artifact_hash}
                </p>
              </div>
            </div>

            {/* Recommendation Reasoning */}
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6">
              <h4 className="text-xs font-mono font-semibold text-on-surface-variant uppercase mb-2">
                CIO Investment Thesis & Allocation Reasoning
              </h4>
              <p className="text-xs text-on-surface leading-relaxed">{recVersion.reasoning}</p>
            </div>

            {/* Target Allocations */}
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6">
              <h4 className="text-xs font-mono font-semibold text-on-surface-variant uppercase mb-4">
                Proposed Asset Allocations ({recVersion.allocations?.length || 0})
              </h4>
              <div className="flex flex-col gap-3">
                {recVersion.allocations?.map((alloc: any) => (
                  <div
                    key={alloc.id}
                    className="p-3 bg-surface-container-low rounded border border-outline-variant/40 flex items-center justify-between text-xs"
                  >
                    <div>
                      <span className="font-bold text-on-surface">{alloc.instrument?.symbol || 'AAPL'}</span>
                      <span className="text-on-surface-variant ml-2">({alloc.rationale})</span>
                    </div>
                    <div className="flex items-center gap-4 font-mono">
                      <span className="text-emerald-400 font-bold">{alloc.side}</span>
                      <span>{(parseFloat(alloc.target_weight) * 100).toFixed(1)}%</span>
                      <span className="text-on-surface-variant">
                        {parseFloat(alloc.target_quantity).toLocaleString()} sh
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Action Panel */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6 flex flex-col gap-4">
              <h3 className="text-sm font-semibold text-on-surface border-b border-outline-variant/30 pb-3">
                Human Approver Attestation
              </h3>

              <div>
                <label className="block text-[11px] font-mono text-on-surface-variant mb-1 uppercase">
                  Legal Attestation Statement
                </label>
                <textarea
                  rows={4}
                  value={attestation}
                  onChange={(e) => setAttestation(e.target.value)}
                  className="w-full bg-surface-container-low border border-outline-variant rounded p-2.5 text-xs text-on-surface focus:outline-none focus:border-secondary"
                />
              </div>

              <div className="flex items-center justify-between bg-surface-container-low p-3 rounded border border-outline-variant/40">
                <span className="text-xs text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-emerald-400 text-base">verified_user</span>
                  MFA Verified
                </span>
                <input
                  type="checkbox"
                  checked={mfaVerified}
                  onChange={(e) => setMfaVerified(e.target.checked)}
                  className="rounded text-secondary focus:ring-0"
                />
              </div>

              <div className="flex flex-col gap-3 pt-2">
                <button
                  onClick={() => handleDecision('APPROVE')}
                  disabled={actionLoading || !mfaVerified}
                  className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded text-xs transition-colors flex items-center justify-center gap-2 shadow-lg shadow-emerald-950/40"
                >
                  <span className="material-symbols-outlined text-base">check_circle</span>
                  APPROVE RECOMMENDATION
                </button>

                <button
                  onClick={() => handleDecision('REJECT')}
                  disabled={actionLoading}
                  className="w-full py-2 bg-error-container hover:bg-error-container/80 text-on-error-container font-semibold rounded text-xs transition-colors flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-base">cancel</span>
                  REJECT RECOMMENDATION
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-12 text-center text-xs text-on-surface-variant">
          No active approval task pending. Submit a recommendation to the approval gate from the Strategy page.
        </div>
      )}
    </div>
  );
}
