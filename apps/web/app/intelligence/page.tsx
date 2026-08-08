'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorBanner } from '@/components/common/ErrorBanner';

export default function IntelligencePage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('');
  const [report, setReport] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = async () => {
    try {
      const wfList = await api.getWorkflows();
      setWorkflows(wfList);
      if (wfList.length > 0) {
        setSelectedWorkflowId(wfList[0].id);
        fetchReport(wfList[0].id);
      } else {
        setLoading(false);
      }
    } catch (err: any) {
      setError('Failed to fetch workflows');
      setLoading(false);
    }
  };

  const fetchReport = async (workflowId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getResearch(workflowId);
      setReport(data);
    } catch (err: any) {
      setReport(null);
      setError('No research report found for selected workflow. Run Market Intelligence Agent from Workflow page.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const latestVersion = report?.versions?.[0];

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex justify-between items-end pb-4 border-b border-outline-variant/50">
        <div>
          <h2 className="font-display text-2xl font-semibold text-on-surface mb-1">
            Market Intelligence Workspace
          </h2>
          <p className="text-sm text-on-surface-variant">
            Verifiable, source-cited equity research reports powered by Market Intelligence Agent
          </p>
        </div>

        {/* Workflow Selector */}
        {workflows.length > 0 && (
          <select
            value={selectedWorkflowId}
            onChange={(e) => {
              setSelectedWorkflowId(e.target.value);
              fetchReport(e.target.value);
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
        <LoadingState message="Loading research report and SEC Form 10-K citations..." />
      ) : latestVersion ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Report Column */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {/* Summary & Metadata Header */}
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6 flex flex-col gap-4">
              <div className="flex justify-between items-center border-b border-outline-variant/30 pb-3">
                <div>
                  <span className="text-[10px] font-mono text-on-surface-variant uppercase tracking-wider">
                    Model: {latestVersion.model_name} ({latestVersion.model_version})
                  </span>
                  <h3 className="text-base font-semibold text-on-surface mt-1">
                    {report.title}
                  </h3>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-mono text-on-surface-variant block uppercase">
                    Confidence
                  </span>
                  <span className="text-lg font-bold text-emerald-400">
                    {(parseFloat(latestVersion.confidence) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-mono font-semibold text-on-surface-variant uppercase mb-2">
                  Market Summary
                </h4>
                <p className="text-xs text-on-surface leading-relaxed">
                  {latestVersion.market_summary}
                </p>
              </div>
            </div>

            {/* Opportunities & Risks Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
                <h4 className="text-xs font-mono font-semibold text-emerald-400 uppercase mb-3 flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm">trending_up</span>
                  Top Opportunities
                </h4>
                <ul className="flex flex-col gap-2">
                  {latestVersion.top_opportunities?.map((opp: string, idx: number) => (
                    <li key={idx} className="text-xs text-on-surface flex items-start gap-2">
                      <span className="text-emerald-400 font-bold">•</span>
                      <span>{opp}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
                <h4 className="text-xs font-mono font-semibold text-amber-400 uppercase mb-3 flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm">warning</span>
                  Top Risks
                </h4>
                <ul className="flex flex-col gap-2">
                  {latestVersion.top_risks?.map((risk: string, idx: number) => (
                    <li key={idx} className="text-xs text-on-surface flex items-start gap-2">
                      <span className="text-amber-400 font-bold">•</span>
                      <span>{risk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Sourced Claims & Citations */}
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-6">
              <h4 className="text-xs font-mono font-semibold text-on-surface-variant uppercase mb-4">
                Empirical Research Claims & SEC EDGAR Citations
              </h4>
              <div className="flex flex-col gap-4">
                {latestVersion.claims?.map((claim: any) => (
                  <div
                    key={claim.id}
                    className="p-4 bg-surface-container-low rounded border border-outline-variant/40 flex flex-col gap-2"
                  >
                    <div className="flex justify-between items-start">
                      <p className="text-xs text-on-surface font-medium">{claim.claim_text}</p>
                      <span className="text-[10px] font-mono text-secondary bg-secondary-container/30 px-2 py-0.5 rounded">
                        Confidence: {(parseFloat(claim.confidence) * 100).toFixed(0)}%
                      </span>
                    </div>

                    {claim.citations?.map((cit: any) => (
                      <div
                        key={cit.id}
                        className="mt-2 p-2 bg-surface-container-high rounded text-[11px] font-mono text-on-surface-variant border border-outline-variant/30"
                      >
                        <div className="flex items-center gap-1.5 text-secondary mb-1">
                          <span className="material-symbols-outlined text-xs">find_in_page</span>
                          <span>{cit.locator}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Sidebar: Company & Sector Ratings */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
              <h4 className="text-xs font-mono font-semibold text-on-surface-variant uppercase mb-3">
                Company Ratings & Targets
              </h4>
              <div className="flex flex-col gap-3">
                {Object.entries(latestVersion.company_analysis || {}).map(([sym, item]: [string, any]) => (
                  <div key={sym} className="p-3 bg-surface-container-low rounded border border-outline-variant/30">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm text-on-surface">{sym}</span>
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold rounded">
                        {item.rating}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface-variant mb-1">{item.thesis}</p>
                    <span className="text-[11px] font-mono text-secondary">Target: ${item.target_price}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-4">
              <h4 className="text-xs font-mono font-semibold text-on-surface-variant uppercase mb-3">
                Sector Allocation Recommendations
              </h4>
              <div className="flex flex-col gap-2">
                {Object.entries(latestVersion.sector_analysis || {}).map(([sec, item]: [string, any]) => (
                  <div key={sec} className="flex justify-between items-center p-2 bg-surface-container-low rounded text-xs">
                    <span className="text-on-surface">{sec}</span>
                    <span className="font-mono text-secondary font-semibold">{item.weight_recommendation}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="border border-outline-variant rounded-lg bg-surface-container-lowest p-12 text-center text-xs text-on-surface-variant">
          No research report available for this workflow. Go to Workflows page to run Market Intelligence.
        </div>
      )}
    </div>
  );
}
