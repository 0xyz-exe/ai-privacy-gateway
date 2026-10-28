export type ViewTab =
  | 'overview'
  | 'playground'
  | 'policies'
  | 'providers'
  | 'keys'
  | 'usage'
  | 'audit-logs'
  | 'settings';

export interface PrivacyPolicy {
  id: number;
  name: string;
  description: string;
  is_enabled: boolean;
  priority: number;
  mode: 'redact' | 'block' | 'allow' | 'redact_and_restore' | 'strict';
  blocked_entities: string[];
  allowed_entities: string[];
  min_confidence: number;
  request_size_limit: number;
  response_scanning: boolean;
  streaming_allowed: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProviderItem {
  id: number;
  name: string;
  provider_type: 'openai' | 'ollama' | 'mock';
  base_url: string;
  api_key_masked: string;
  is_active: boolean;
  is_default: boolean;
  timeout_seconds: number;
  models: string[];
  created_at: string;
}

export interface APIKeyItem {
  id: number;
  name: string;
  prefix: string;
  is_active: boolean;
  policy_id: number | null;
  rate_limit: number;
  created_at: string;
  last_used_at: string | null;
}

export interface AuditEventItem {
  id: number;
  request_id: string;
  timestamp: string;
  key_prefix: string;
  provider: string;
  model: string;
  duration_ms: number;
  tokens_used: number;
  redaction_count: number;
  detected_entities: string[];
  policy_decision: 'allowed' | 'redacted' | 'blocked';
  http_status: number;
  error_code: string | null;
}

export interface UsageSummary {
  total_requests: number;
  blocked_requests: number;
  total_redactions: number;
  total_tokens: number;
  avg_latency_ms: number;
  estimated_cost_usd: number;
  provider_breakdown: Record<string, number>;
  entity_frequency: Record<string, number>;
}

export interface DetectedEntity {
  entity_type: string;
  text: string;
  start: number;
  end: number;
  confidence: number;
  recognizer_id: string;
}

export interface PlaygroundResult {
  original_text: string;
  redacted_text: string;
  restored_preview: string;
  detected_entities: DetectedEntity[];
  policy_decision: string;
  policy_reason: string;
  redaction_count: number;
  entity_summary: Record<string, number>;
  outbound_payload_preview: string;
}
