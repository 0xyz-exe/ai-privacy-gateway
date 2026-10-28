import React, { useEffect, useState } from 'react';
import { Shield, ShieldAlert, Cpu, Activity, Lock, ArrowUpRight } from 'lucide-react';
import { api } from '../api';
import type { UsageSummary, AuditEventItem, ViewTab } from '../types';

export const OverviewView: React.FC<{ onNavigate: (tab: ViewTab) => void }> = ({ onNavigate }) => {
  const [summary, setSummary] = useState<UsageSummary | null>(null);
  const [recentLogs, setRecentLogs] = useState<AuditEventItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sumRes, logsRes] = await Promise.all([
          api.getUsageSummary(),
          api.getAuditLogs({ limit: 5 })
        ]);
        setSummary(sumRes);
        setRecentLogs(logsRes.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Hero Banner */}
      <div className="rounded-xl border border-slate-800 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-medium text-sm mb-1">
              <Shield className="w-4 h-4" />
              <span>AI Privacy & Data Loss Prevention Layer</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">AI Privacy Gateway</h1>
            <p className="text-slate-400 text-sm mt-1 max-w-2xl">
              Intercepts LLM requests, detects & redacts sensitive PII and secrets, enforces strict privacy policies, and sanitizes upstream AI responses.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate('playground')}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-indigo-500/20 flex items-center gap-1.5"
            >
              <span>Launch Playground</span>
              <ArrowUpRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('keys')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg font-medium text-sm transition-colors"
            >
              Generate API Key
            </button>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Total Requests</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {loading ? '...' : (summary?.total_requests ?? 0).toLocaleString()}
          </div>
          <p className="text-xs text-slate-500 mt-1">Processed through gateway</p>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">PII Redactions</span>
            <Lock className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-indigo-400">
            {loading ? '...' : (summary?.total_redactions ?? 0).toLocaleString()}
          </div>
          <p className="text-xs text-slate-500 mt-1">Values sanitized from prompts</p>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Policy Blocks</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-400">
            {loading ? '...' : (summary?.blocked_requests ?? 0).toLocaleString()}
          </div>
          <p className="text-xs text-slate-500 mt-1">Violations rejected before upstream</p>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Avg Latency</span>
            <Cpu className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {loading ? '...' : `${summary?.avg_latency_ms ?? 0} ms`}
          </div>
          <p className="text-xs text-slate-500 mt-1">Inspection & proxy overhead</p>
        </div>
      </div>

      {/* Grid: Provider breakdown & Entity Frequency */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-base font-semibold text-white mb-4">Detected PII Categories</h2>
          {loading ? (
            <div className="text-sm text-slate-500 py-6 text-center">Loading categories...</div>
          ) : Object.keys(summary?.entity_frequency || {}).length === 0 ? (
            <div className="text-sm text-slate-500 py-8 text-center border border-dashed border-slate-800 rounded-lg">
              No PII events detected yet. Test in Playground to see detections.
            </div>
          ) : (
            <div className="space-y-3">
              {Object.entries(summary?.entity_frequency || {}).map(([ent, count]) => (
                <div key={ent} className="flex items-center justify-between text-sm">
                  <span className="font-mono text-xs px-2 py-1 rounded bg-slate-800 text-indigo-300 border border-slate-700">
                    {ent}
                  </span>
                  <span className="text-slate-300 font-semibold">{count}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-base font-semibold text-white mb-4">Active Providers</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/40 border border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                <div>
                  <div className="text-sm font-medium text-white">Local Mock Engine</div>
                  <div className="text-xs text-slate-400">Zero-cost internal testing adapter</div>
                </div>
              </div>
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                Active Default
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/40 border border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-blue-400" />
                <div>
                  <div className="text-sm font-medium text-white">Ollama Local Inference</div>
                  <div className="text-xs text-slate-400">http://localhost:11434/v1</div>
                </div>
              </div>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                Ready
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/40 border border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-purple-400" />
                <div>
                  <div className="text-sm font-medium text-white">OpenAI Cloud</div>
                  <div className="text-xs text-slate-400">https://api.openai.com/v1</div>
                </div>
              </div>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                Configurable
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Sanitized Audit Activity */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-white">Recent Audit Events (Sanitized)</h2>
          <button
            onClick={() => onNavigate('audit-logs')}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
          >
            View all logs →
          </button>
        </div>

        {recentLogs.length === 0 ? (
          <div className="text-center py-8 text-sm text-slate-500 border border-dashed border-slate-800 rounded-lg">
            No audit events recorded yet. Run a prompt in Playground or send an API request.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase bg-slate-800/60 text-slate-400">
                <tr>
                  <th className="py-2.5 px-3 rounded-l">Request ID</th>
                  <th className="py-2.5 px-3">Provider</th>
                  <th className="py-2.5 px-3">Decision</th>
                  <th className="py-2.5 px-3">Redactions</th>
                  <th className="py-2.5 px-3">Latency</th>
                  <th className="py-2.5 px-3 rounded-r">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {recentLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-mono text-xs text-slate-300">{log.request_id}</td>
                    <td className="py-2.5 px-3 text-slate-300">{log.provider}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`text-xs px-2 py-0.5 rounded font-medium border ${
                          log.policy_decision === 'blocked'
                            ? 'bg-rose-950/80 text-rose-300 border-rose-800'
                            : log.policy_decision === 'redacted'
                            ? 'bg-indigo-950/80 text-indigo-300 border-indigo-800'
                            : 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                        }`}
                      >
                        {log.policy_decision}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-300">{log.redaction_count}</td>
                    <td className="py-2.5 px-3 text-slate-400">{log.duration_ms} ms</td>
                    <td className="py-2.5 px-3">
                      <span className="text-xs text-slate-300">{log.http_status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
