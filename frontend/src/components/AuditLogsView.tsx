import React, { useEffect, useState } from 'react';
import { FileText, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../api';
import type { AuditEventItem } from '../types';

export const AuditLogsView: React.FC = () => {
  const [logs, setLogs] = useState<AuditEventItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [decisionFilter, setDecisionFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const limit = 20;

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs({
        limit,
        offset: page * limit,
        decision: decisionFilter || undefined,
      });
      setLogs(data.items || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, decisionFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <span>Privacy Audit Logs</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Privacy-preserving audit trail. Metadata and detection events are recorded; raw prompts and original PII are strictly excluded.
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-3">
          <select
            value={decisionFilter}
            onChange={(e) => {
              setDecisionFilter(e.target.value);
              setPage(0);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Decisions</option>
            <option value="redacted">Redacted</option>
            <option value="blocked">Blocked</option>
            <option value="allowed">Allowed</option>
          </select>
          <button
            onClick={fetchLogs}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-xs text-slate-400 uppercase">
              <tr>
                <th className="py-3 px-4">Request ID</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Key Prefix</th>
                <th className="py-3 px-4">Provider / Model</th>
                <th className="py-3 px-4">Decision</th>
                <th className="py-3 px-4">Detected PII Categories</th>
                <th className="py-3 px-4">Redactions</th>
                <th className="py-3 px-4">Latency</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-xs">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-500">
                    Loading audit trail...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-500">
                    No audit events match current filters.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30">
                    <td className="py-3 px-4 font-mono text-slate-300">{log.request_id}</td>
                    <td className="py-3 px-4 text-slate-400">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400">{log.key_prefix}</td>
                    <td className="py-3 px-4 text-slate-300">
                      <div className="font-medium">{log.provider}</div>
                      <div className="text-[10px] text-slate-500">{log.model}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded font-medium border text-[11px] ${
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
                    <td className="py-3 px-4">
                      {log.detected_entities && log.detected_entities.length > 0 ? (
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {log.detected_entities.map((cat, idx) => (
                            <span
                              key={idx}
                              className="px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 text-[10px] font-mono border border-slate-700"
                            >
                              {cat}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-600">None</span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-300">{log.redaction_count}</td>
                    <td className="py-3 px-4 text-slate-400">{log.duration_ms} ms</td>
                    <td className="py-3 px-4">
                      <span
                        className={`font-mono text-xs ${
                          log.http_status >= 400 ? 'text-rose-400' : 'text-emerald-400'
                        }`}
                      >
                        {log.http_status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination footer */}
        <div className="p-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>
            Showing {logs.length} of {total} events
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="p-1 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono">Page {page + 1}</span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * limit >= total}
              className="p-1 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
