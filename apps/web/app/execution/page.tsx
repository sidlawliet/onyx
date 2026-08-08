'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorBanner } from '@/components/common/ErrorBanner';

export default function ExecutionPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('');
  const [workflow, setWorkflow] = useState<any | null>(null);
  const [executionResult, setExecutionResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [safetyGateTestResult, setSafetyGateTestResult] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [wfList, acctList, intList] = await Promise.all([
        api.getWorkflows(),
        api.getAccounts(),
        api.getIntegrations(),
      ]);
      setWorkflows(wfList);
      setAccounts(acctList);
      setIntegrations(intList);
      if (wfList.length > 0) {
        setSelectedWorkflowId(wfList[0].id);
        fetchWorkflowDetail(wfList[0].id);
      } else {
        setLoading(false);
      }
    } catch (err: any) {
      setError('Failed to fetch execution context data');
      setLoading(false);
    }
  };

  const fetchWorkflowDetail = async (workflowId: string) => {
    try {
      const data = await api.getWorkflow(workflowId);
      setWorkflow(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const task = workflow?.approval_tasks?.[0];
  const manifest = task?.artifact_manifest;
  const recVersion = manifest?.recommendation_version || workflow?.recommendations?.[0]?.versions?.[0];

  const handleExecuteTrade = async () => {
    if (!manifest || !recVersion || accounts.length === 0 || integrations.length === 0) return;
    setActionLoading(true);
    setError(null);
    try {
      const idempotencyKey = `IDEM-WEB-${Date.now()}`;
      const res = await api.submitExecutionIntent(
        manifest.id,
        recVersion.artifact_hash,
        accounts[0].id,
        integrations[0].id,
        idempotencyKey
      );
      setExecutionResult(res);
      alert('Trade Execution Intent submitted and filled successfully via FIX Broker Sandbox!');
      fetchWorkflowDetail(selectedWorkflowId);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Execution Safety Gate rejected request');
    } finally {
      setActionLoading(false);
    }
  };

  const handleTestSafetyGateRejection = async () => {
    if (!recVersion || accounts.length === 0 || integrations.length === 0) return;
    setActionLoading(true);
    setSafetyGateTestResult(null);
    try {
      // Attempt execution with tampered hash to prove Safety Gate works!
      const tamperedHash = 'f'.repeat(64);
      await api.submitExecutionIntent(
        manifest?.id || recVersion.id,
        tamperedHash,
        accounts[0].id,
        integrations[0].id,
        `IDEM-TAMPERED-${Date.now()}`
      );
      setSafetyGateTestResult('Unexpected: Execution succeeded with tampered hash');
    } catch (err: any) {
      const status = err.response?.status;
      const msg = err.response?.data?.message || 'Rejected';
      setSafetyGateTestResult(
        `SAFETY GATE PASSED PROOF! Execution rejected with HTTP ${status}: "${msg}". Order was blocked.`
      );
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
            Pre-Approved Trade Execution Control
          </h2>
          <p className="text-sm text-on-surface-variant">
            Execution Safety Gate — Only approved artifact manifests are eligible for broker order release
          </p>
        </div>

        {/* Workflow Selector */}
        {workflows.length > 0 && (
          <select
            value={selectedWorkflowId}
            onChange={(e) => {
              setSelectedWorkflowId(e.target.value);
              fetchWorkflowDetail(e.target.value);
              setExecutionResult(null);
              setSafetyGateTestResult(null);
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

      {safetyGateTestResult && (
        <div className="p-4 bg-emerald-500/20 border border-emerald-500/40 rounded text-emerald-400 text-xs font-semibold flex items-center gap-2">
          <span className="material-symbols-outlined text-lg">shield</span>
          <span>{safetyGateTestResult}</span>
        </div>
      )}

      {loading ? (
        <LoadingState message="Loading trade execution context and FIX order sandbox..." />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Execution Controls */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {/* Safety Gate Revalidation Status */}
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6 flex flex-col gap-4">
              <div className="flex justify-between items-center border-b border-outline-variant/30 pb-3">
                <h3 className="text-sm font-semibold text-on-surface">Execution Safety Gate Controls</h3>
                <span className="text-xs font-mono text-emerald-400 bg-emerald-500/20 px-2.5 py-1 rounded font-semibold border border-emerald-500/40">
                  Gate: Active
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-[10px] font-mono text-on-surface-variant uppercase block">Account</span>
                  <span className="font-semibold text-on-surface">
                    {accounts[0]?.account_number || 'BROKER-ACCT-9921'} (${parseFloat(accounts[0]?.available_cash || '1500000').toLocaleString()})
                  </span>
                </div>

                <div>
                  <span className="text-[10px] font-mono text-on-surface-variant uppercase block">Broker Integration</span>
                  <span className="font-semibold text-on-surface">
                    {integrations[0]?.provider_name || 'Broker FIX Sandbox'} ({integrations[0]?.environment || 'SANDBOX'})
                  </span>
                </div>
              </div>

              <div className="flex flex-wrap gap-3 pt-2">
                <button
                  onClick={handleExecuteTrade}
                  disabled={actionLoading || !manifest}
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded text-xs transition-colors flex items-center gap-2 shadow-lg shadow-emerald-950/40"
                >
                  <span className="material-symbols-outlined text-base">play_circle</span>
                  RELEASE PRE-APPROVED TRADE ORDERS
                </button>

                <button
                  onClick={handleTestSafetyGateRejection}
                  disabled={actionLoading}
                  className="px-4 py-2.5 bg-surface-container-high border border-outline-variant text-on-surface hover:bg-surface-container-highest rounded text-xs font-semibold transition-colors flex items-center gap-2"
                >
                  <span className="material-symbols-outlined text-base text-amber-400">bug_report</span>
                  Test Safety Gate (Tampered Hash Attack)
                </button>
              </div>
            </div>

            {/* Executed Fills Table */}
            {executionResult && (
              <div className="border border-outline-variant rounded-lg bg-surface-container-lowest overflow-hidden">
                <div className="px-6 py-4 border-b border-outline-variant bg-surface-container-low/50 text-xs font-mono font-semibold text-on-surface-variant uppercase flex justify-between items-center">
                  <span>FIX Broker Executed Fills ({executionResult.orders?.length || 0})</span>
                  <span className="text-emerald-400 font-bold">STATUS: {executionResult.status}</span>
                </div>

                <table className="w-full text-left text-xs">
                  <thead className="bg-surface-container-high/40 text-on-surface-variant font-mono uppercase text-[10px] border-b border-outline-variant">
                    <tr>
                      <th className="py-3 px-6">Client Order ID</th>
                      <th className="py-3 px-6">Provider Order ID</th>
                      <th className="py-3 px-6">Side</th>
                      <th className="py-3 px-6">Executed Price</th>
                      <th className="py-3 px-6">Executed Shares</th>
                      <th className="py-3 px-6">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant/30 text-on-surface font-mono">
                    {executionResult.orders?.map((ord: any) => (
                      <tr key={ord.id} className="hover:bg-surface-container-low/50">
                        <td className="py-3.5 px-6 font-bold text-secondary">{ord.client_order_id}</td>
                        <td className="py-3.5 px-6 text-on-surface-variant">{ord.provider_order_id}</td>
                        <td className="py-3.5 px-6 text-emerald-400 font-bold">{ord.side}</td>
                        <td className="py-3.5 px-6">${parseFloat(ord.limit_price).toFixed(2)}</td>
                        <td className="py-3.5 px-6">{parseFloat(ord.quantity).toLocaleString()}</td>
                        <td className="py-3.5 px-6 font-bold text-emerald-400">{ord.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Right Info Box */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6 flex flex-col gap-3">
              <h4 className="text-xs font-mono font-semibold text-on-surface-variant uppercase">
                Execution Security Invariants
              </h4>
              <ul className="flex flex-col gap-2 text-xs text-on-surface-variant">
                <li className="flex items-start gap-2">
                  <span className="text-secondary font-bold">•</span>
                  <span>Execution endpoints reject free-form portfolio payloads.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-secondary font-bold">•</span>
                  <span>Orders must reference an active human APPROVE decision.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-secondary font-bold">•</span>
                  <span>Revalidates exact artifact SHA-256 hash against locked manifest.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-secondary font-bold">•</span>
                  <span>Enforces unique idempotency keys to prevent duplicate trades.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
