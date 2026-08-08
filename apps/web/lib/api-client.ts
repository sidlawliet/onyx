import axios from 'axios';

const API_BASE_URL = typeof window !== 'undefined' 
  ? '/api/v1' 
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('investops_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const api = {
  // Auth
  login: async (email: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', 'demo1234');
    const res = await apiClient.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return res.data;
  },
  getCurrentUser: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },

  // Portfolios & Accounts
  getPortfolios: async () => {
    const res = await apiClient.get('/portfolios');
    return res.data;
  },
  getAccounts: async () => {
    const res = await apiClient.get('/portfolios/accounts');
    return res.data;
  },
  getHoldings: async (portfolioId: string) => {
    const res = await apiClient.get(`/portfolios/${portfolioId}/holdings`);
    return res.data;
  },

  // Workflows
  getWorkflows: async () => {
    const res = await apiClient.get('/workflows');
    return res.data;
  },
  getWorkflow: async (id: string) => {
    const res = await apiClient.get(`/workflows/${id}`);
    return res.data;
  },
  createWorkflow: async (portfolioId: string, title: string) => {
    const res = await apiClient.post('/workflows', { portfolio_id: portfolioId, title });
    return res.data;
  },

  // Market Intelligence
  runResearch: async (workflowId: string) => {
    const res = await apiClient.post(`/research-reports/workflows/${workflowId}/run`);
    return res.data;
  },
  getResearch: async (workflowId: string) => {
    const res = await apiClient.get(`/research-reports/workflows/${workflowId}`);
    return res.data;
  },

  // Portfolio Strategy
  generateRecommendation: async (workflowId: string) => {
    const res = await apiClient.post(`/recommendations/workflows/${workflowId}/generate`);
    return res.data;
  },
  validateRecommendation: async (recommendationVersionId: string) => {
    const res = await apiClient.post(`/recommendations/versions/${recommendationVersionId}/validate`);
    return res.data;
  },

  // Human Approval Gate
  submitForApproval: async (recommendationVersionId: string) => {
    const res = await apiClient.post(`/approval-tasks/recommendation-versions/${recommendationVersionId}/submit`);
    return res.data;
  },
  submitApprovalDecision: async (taskId: string, decision: 'APPROVE' | 'REJECT', attestation: string, artifactHash: string) => {
    const res = await apiClient.post(`/approval-tasks/tasks/${taskId}/decision`, {
      decision,
      attestation,
      artifact_hash: artifactHash,
      mfa_verified: true,
    });
    return res.data;
  },

  // Pre-Approved Execution
  submitExecutionIntent: async (manifestId: string, artifactHash: string, accountId: string, integrationId: string, idempotencyKey: string) => {
    const res = await apiClient.post('/execution-intents', {
      approved_artifact_id: manifestId,
      approved_artifact_hash: artifactHash,
      account_id: accountId,
      integration_id: integrationId,
      idempotency_key: idempotencyKey,
    });
    return res.data;
  },

  // Portfolio Monitoring
  captureSnapshots: async (portfolioId: string) => {
    const res = await apiClient.post(`/monitoring/portfolios/${portfolioId}/capture-snapshots`);
    return res.data;
  },
  getAlerts: async (portfolioId: string) => {
    const res = await apiClient.get(`/monitoring/portfolios/${portfolioId}/alerts`);
    return res.data;
  },

  // Integrations
  getIntegrations: async () => {
    const res = await apiClient.get('/integrations');
    return res.data;
  },

  // Audit Events
  getAuditEvents: async (traceId?: string) => {
    const url = traceId ? `/audit-events/events?trace_id=${traceId}` : '/audit-events/events';
    const res = await apiClient.get(url);
    return res.data;
  },
  exportAuditChain: async (traceId?: string) => {
    const res = await apiClient.post('/audit-events/export', { trace_id: traceId });
    return res.data;
  },

  // System Health & Agents
  getSystemHealth: async () => {
    const res = await apiClient.get('/system-health');
    return res.data;
  },
  getAgentsStatus: async () => {
    const res = await apiClient.get('/agents/status');
    return res.data;
  },
};
