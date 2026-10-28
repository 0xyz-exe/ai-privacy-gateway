import React, { useEffect, useState } from 'react';
import { BarChart3, DollarSign, Database, Activity, RefreshCw } from 'lucide-react';
import { api } from '../api';
import type { UsageSummary } from '../types';

export const UsageView: React.FC = () => {
  const [summary, setSummary] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUsage = async () => {
    setLoading(true);
    try {
      const data = await api.getUsageSummary();
      setSummary(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsage();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-indigo-400" />
            <span>Usage Analytics & Cost Estimates</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Track traffic volume, token throughput, and estimated upstream provider costs. Figures are estimates based on standard blended rates.
          </p>
        </div>
        <button
          onClick={fetchUsage}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Estimated Cost</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-emerald-400">
            ${summary?.estimated_cost_usd?.toFixed(4) ?? '0.0000'}
          </div>
          <p className="text-[11px] text-slate-500 mt-2">
            Based on blended rate of $5.00 / 1M tokens processed upstream.
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Tokens</span>
            <Database className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-3xl font-bold text-white">
            {summary?.total_tokens?.toLocaleString() ?? 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-2">Prompt and completion tokens combined.</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Redactions</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-bold text-purple-400">
            {summary?.total_redactions?.toLocaleString() ?? 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-2">Sensitive entities anonymized before forwarding.</p>
        </div>
      </div>

      {/* Breakdown grids */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-base font-semibold text-white mb-4">Traffic by Provider</h2>
          {Object.keys(summary?.provider_breakdown || {}).length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500 border border-dashed border-slate-800 rounded-lg">
              No provider activity recorded yet.
            </div>
          ) : (
            <div className="space-y-3">
              {Object.entries(summary?.provider_breakdown || {}).map(([provider, count]) => {
                const pct = summary?.total_requests ? Math.round((count / summary.total_requests) * 100) : 0;
                return (
                  <div key={provider} className="space-y-1">
                    <div className="flex justify-between text-xs text-slate-300">
                      <span className="font-medium capitalize">{provider}</span>
                      <span className="font-mono text-slate-400">{count} requests ({pct}%)</span>
                    </div>
                    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-500 rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-base font-semibold text-white mb-4">Detected PII Distribution</h2>
          {Object.keys(summary?.entity_frequency || {}).length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500 border border-dashed border-slate-800 rounded-lg">
              No PII frequency data available yet.
            </div>
          ) : (
            <div className="space-y-3">
              {Object.entries(summary?.entity_frequency || {}).map(([entity, count]) => (
                <div key={entity} className="flex items-center justify-between text-xs">
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 font-mono border border-slate-700">
                    {entity}
                  </span>
                  <span className="font-bold text-slate-200">{count} detected</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
