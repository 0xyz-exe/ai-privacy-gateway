import type {
  PrivacyPolicy, ProviderItem, APIKeyItem, AuditEventItem,
  UsageSummary, PlaygroundResult
} from './types';

const API_BASE = ''; // Proxied by Vite to http://127.0.0.1:8000

export const getAdminToken = () => localStorage.getItem('aipg_admin_token') || 'admin-secret-token-demo';
export const setAdminToken = (token: string) => localStorage.setItem('aipg_admin_token', token);

const headers = (requireAdmin: boolean = false) => {
  const h: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (requireAdmin) {
    h['X-Admin-Token'] = getAdminToken();
  }
  return h;
};

export const api = {
  // Health
  getHealth: async () => {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  // Playground
  analyzePlayground: async (data: {
    text: string;
    mode: string;
    min_confidence: number;
    blocked_entities: string[];
    allowed_entities: string[];
  }): Promise<PlaygroundResult> => {
    const res = await fetch(`${API_BASE}/api/playground/analyze`, {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to analyze');
    return res.json();
  },

  // Policies
  getPolicies: async (): Promise<PrivacyPolicy[]> => {
    const res = await fetch(`${API_BASE}/api/policies`, { headers: headers() });
    return res.json();
  },
  createPolicy: async (data: Partial<PrivacyPolicy>): Promise<PrivacyPolicy> => {
    const res = await fetch(`${API_BASE}/api/policies`, {
      method: 'POST',
      headers: headers(true),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to create policy');
    return res.json();
  },
  updatePolicy: async (id: number, data: Partial<PrivacyPolicy>): Promise<PrivacyPolicy> => {
    const res = await fetch(`${API_BASE}/api/policies/${id}`, {
      method: 'PUT',
      headers: headers(true),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to update policy');
    return res.json();
  },
  deletePolicy: async (id: number) => {
    const res = await fetch(`${API_BASE}/api/policies/${id}`, {
      method: 'DELETE',
      headers: headers(true),
    });
    return res.json();
  },

  // Providers
  getProviders: async (): Promise<ProviderItem[]> => {
    const res = await fetch(`${API_BASE}/api/providers`, { headers: headers() });
    return res.json();
  },
  createProvider: async (data: any): Promise<ProviderItem> => {
    const res = await fetch(`${API_BASE}/api/providers`, {
      method: 'POST',
      headers: headers(true),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to create provider');
    return res.json();
  },
  testProvider: async (id: number) => {
    const res = await fetch(`${API_BASE}/api/providers/${id}/test`, {
      method: 'POST',
      headers: headers(true),
    });
    return res.json();
  },
  deleteProvider: async (id: number) => {
    const res = await fetch(`${API_BASE}/api/providers/${id}`, {
      method: 'DELETE',
      headers: headers(true),
    });
    return res.json();
  },

  // Keys
  getKeys: async (): Promise<APIKeyItem[]> => {
    const res = await fetch(`${API_BASE}/api/keys`, { headers: headers(true) });
    return res.json();
  },
  createKey: async (data: { name: string; policy_id?: number; rate_limit?: number }) => {
    const res = await fetch(`${API_BASE}/api/keys`, {
      method: 'POST',
      headers: headers(true),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to create key');
    return res.json();
  },
  revokeKey: async (id: number) => {
    const res = await fetch(`${API_BASE}/api/keys/${id}`, {
      method: 'DELETE',
      headers: headers(true),
    });
    return res.json();
  },

  // Audit Logs
  getAuditLogs: async (params: { limit?: number; offset?: number; decision?: string }): Promise<{ total: number; items: AuditEventItem[] }> => {
    const q = new URLSearchParams();
    if (params.limit) q.set('limit', String(params.limit));
    if (params.offset) q.set('offset', String(params.offset));
    if (params.decision) q.set('decision', params.decision);
    const res = await fetch(`${API_BASE}/api/audit-logs?${q.toString()}`, { headers: headers(true) });
    return res.json();
  },

  // Usage
  getUsageSummary: async (): Promise<UsageSummary> => {
    const res = await fetch(`${API_BASE}/api/usage/summary`, { headers: headers() });
    return res.json();
  },

  // Settings
  getSettings: async () => {
    const res = await fetch(`${API_BASE}/api/settings`, { headers: headers() });
    return res.json();
  },
};
