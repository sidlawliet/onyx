'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorBanner } from '@/components/common/ErrorBanner';

interface WorkflowItem {
  id: string;
  tenant_id: string;
  portfolio_id: string;
  title: string;
  stage: string;
  status: string;
  trace_id: string;
  created_at: string;
}

export default function WorkflowPage() {
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([]);
  const [portfolios, setPortfolios] = useState<any[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [wfData, portData] = await Promise.all([
        api.getWorkflows(),
        api.getPortfolios(),
      ]);
      setWorkflows(wfData);
      setPortfolios(portData);
      if (wfData.length > 0 && !selectedWorkflow) {
        setSelectedWorkflow(wfData[0]);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.message || 'Failed to load workflow pipelines');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateWorkflow = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || portfolios.length === 0) return;
    setActionLoading(true);
    try {
      const created = await api.createWorkflow(portfolios[0].id, newTitle);
      setWorkflows([created, ...workflows]);
      setSelectedWorkflow(created);
      setNewTitle('');
      setShowCreateModal(false);
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to create workflow');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRunIntelligence = async (workflowId: string) => {
    setActionLoading(true);
    try {
      await api.runResearch(workflowId);
      await fetchData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to run Market Intelligence Agent');
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateStrategy = async (workflowId: string) => {
    setActionLoading(true);
    try {
      await api.generateRecommendation(workflowId);
      await fetchData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to generate Portfolio Strategy Recommendation');
    } finally {
      setActionLoading(false);
    }
  };

  const stages = [
    { key: 'MARKET_INTELLIGENCE', label: '1. Market Intelligence' },
    { key: 'PORTFOLIO_STRATEGY', label: '2. Portfolio Strategy' },
    { key: 'HUMAN_APPROVAL', label: '3. Human Approval' },
    { key: 'TRADE_EXECUTION', label: '4. Trade Execution' },
    { key: 'PORTFOLIO_MONITORING', label: '5. Portfolio Monitoring' },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex justify-between items-end pb-4 border-b border-outline-variant/50">
        <div>
          <h2 className="font-display text-2xl font-semibold text-on-surface mb-1">
            Active Workflow Pipelines
          </h2>
          <p className="text-sm text-on-surface-variant">
            5-Stage Institutional Investment Workflow Engine & Trace Context
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-secondary-container text-on-secondary-container hover:bg-secondary-container/80 rounded transition-colors text-xs font-semibold flex items-center gap-2"
        >
          <span className="material-symbols-outlined text-base">add</span>
          New Rebalance Workflow
        </button>
      </div>

      {error && <ErrorBanner message={error} onRetry={fetchData} />}

      {loading ? (
        <LoadingState message="Loading active workflow pipelines..." />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Workflows List Column */}
          <div className="lg:col-span-1 flex flex-col border border-outline-variant rounded-lg bg-surface-container-lowest overflow-hidden">
            <div className="px-4 py-3 border-b border-outline-variant bg-surface-container-low/50 text-xs font-mono font-semibold text-on-surface-variant uppercase tracking-wider">
              Pipelines ({workflows.length})
            </div>
            <div className="divide-y divide-outline-variant/30 overflow-y-auto max-h-[600px]">
              {workflows.map((wf) => {
                const isSelected = selectedWorkflow?.id === wf.id;
                return (
                  <div
                    key={wf.id}
                    onClick={() => setSelectedWorkflow(wf)}
                    className={`p-4 cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-surface-container-low border-l-2 border-secondary'
                        : 'hover:bg-surface-container-low/50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono text-[11px] text-on-surface-variant">
                        {wf.id.substring(0, 8)}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-surface-container-high text-secondary border border-outline-variant/50">
                        {wf.stage}
                      </span>
                    </div>
                    <h4 className="text-sm font-semibold text-on-surface mb-1">{wf.title}</h4>
                    <div className="flex items-center justify-between text-[11px] text-on-surface-variant">
                      <span>Status: {wf.status}</span>
                      <span className="font-mono">{new Date(wf.created_at).toLocaleTimeString()}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Workflow Detail & Stage Timeline Column */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {selectedWorkflow ? (
              <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6 flex flex-col gap-6">
                <div className="flex justify-between items-start border-b border-outline-variant/40 pb-4">
                  <div>
                    <span className="text-xs font-mono text-on-surface-variant">
                      Trace ID: {selectedWorkflow.trace_id}
                    </span>
                    <h3 className="text-lg font-semibold text-on-surface mt-1">
                      {selectedWorkflow.title}
                    </h3>
                  </div>
                  <div className="flex gap-2">
                    {selectedWorkflow.stage === 'MARKET_INTELLIGENCE' && (
                      <button
                        onClick={() => handleRunIntelligence(selectedWorkflow.id)}
                        disabled={actionLoading}
                        className="px-3 py-1.5 bg-secondary-container text-on-secondary-container rounded hover:bg-secondary-container/80 text-xs font-semibold transition-colors flex items-center gap-1.5"
                      >
                        <span className="material-symbols-outlined text-base">psychology</span>
                        Run Market Intelligence Agent
                      </button>
                    )}
                    {selectedWorkflow.stage === 'PORTFOLIO_STRATEGY' && (
                      <button
                        onClick={() => handleGenerateStrategy(selectedWorkflow.id)}
                        disabled={actionLoading}
                        className="px-3 py-1.5 bg-secondary-container text-on-secondary-container rounded hover:bg-secondary-container/80 text-xs font-semibold transition-colors flex items-center gap-1.5"
                      >
                        <span className="material-symbols-outlined text-base">insights</span>
                        Generate Portfolio Strategy
                      </button>
                    )}
                  </div>
                </div>

                {/* 5-Stage Institutional Timeline */}
                <div>
                  <h4 className="text-xs font-mono text-on-surface-variant uppercase tracking-wider mb-4">
                    Institutional Stage State Machine
                  </h4>
                  <div className="flex flex-col gap-3">
                    {stages.map((stg, idx) => {
                      const currentIdx = stages.findIndex((s) => s.key === selectedWorkflow.stage);
                      const isPast = idx < currentIdx;
                      const isCurrent = idx === currentIdx;

                      return (
                        <div
                          key={stg.key}
                          className={`p-3 rounded border flex items-center justify-between text-xs transition-colors ${
                            isCurrent
                              ? 'bg-surface-container-low border-secondary text-secondary font-semibold'
                              : isPast
                              ? 'bg-surface-container/40 border-outline-variant/30 text-on-surface-variant'
                              : 'bg-surface-container-lowest border-outline-variant/20 text-on-surface-variant/40'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <span className="material-symbols-outlined text-lg">
                              {isPast
                                ? 'check_circle'
                                : isCurrent
                                ? 'pending'
                                : 'radio_button_unchecked'}
                            </span>
                            <span>{stg.label}</span>
                          </div>

                          <span className="font-mono text-[11px]">
                            {isCurrent
                              ? selectedWorkflow.status
                              : isPast
                              ? 'COMPLETED'
                              : 'PENDING'}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-12 text-center text-xs text-on-surface-variant">
                Select a workflow pipeline from the left to view stage timeline.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest border border-outline-variant rounded-lg max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-base font-semibold text-on-surface mb-4">Initiate New Rebalance Workflow</h3>
            <form onSubmit={handleCreateWorkflow} className="flex flex-col gap-4">
              <div>
                <label className="block text-xs text-on-surface-variant mb-1 font-medium">
                  Workflow Title
                </label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Q4 Institutional Tech Rebalance"
                  className="w-full bg-surface-container-low border border-outline-variant rounded px-3 py-2 text-xs text-on-surface focus:outline-none focus:border-secondary"
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 border border-outline-variant rounded text-xs text-on-surface-variant hover:text-on-surface"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-4 py-1.5 bg-secondary-container text-on-secondary-container rounded text-xs font-semibold hover:bg-secondary-container/80"
                >
                  Create Pipeline
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
