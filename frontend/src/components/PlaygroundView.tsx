import React, { useState } from 'react';
import { Play, Sparkles, Trash2, ShieldCheck, ShieldAlert, Lock, RefreshCw } from 'lucide-react';
import { api } from '../api';
import type { PlaygroundResult } from '../types';

const PRESETS = [
  {
    name: 'Standard Example',
    text: 'Please send the invoice to alice@example.com and contact me at +62 812-3456-7890.',
    mode: 'redact',
  },
  {
    name: 'Indonesian Identity & Banking',
    text: 'Kirimkan data ke budi.santoso@perusahaan.co.id. No HP: +62 812-3456-7890, Rekening BCA 1234567890. NIK KTP: 3201011508900001 dan NPWP: 01.234.567.8-123.000.',
    mode: 'redact_and_restore',
  },
  {
    name: 'Financial & Credit Cards',
    text: 'Please charge Visa card 4111-1111-1111-1111 and verify IBAN DE89370400440532013000. Send receipt to accounting@bank.com.',
    mode: 'block',
  },
  {
    name: 'Cloud & API Secrets',
    text: 'Debug connection using OpenAI token sk-proj-1234567890abcdefghijklmnopqrstuvwxyz and AWS Access Key AKIAIOSFODNN7EXAMPLE on server 192.168.1.50.',
    mode: 'strict',
  },
];

export const PlaygroundView: React.FC = () => {
  const [inputText, setInputText] = useState(PRESETS[0].text);
  const [mode, setMode] = useState<string>('redact');
  const [minConfidence, setMinConfidence] = useState<number>(0.70);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PlaygroundResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.analyzePlayground({
        text: inputText,
        mode,
        min_confidence: minConfidence,
        blocked_entities: mode === 'block' ? ['CREDIT_CARD', 'NIK', 'API_KEY', 'SECRET_KEY'] : [],
        allowed_entities: [],
      });
      setResult(res);
    } catch (e: any) {
      setError(e.message || 'Failed to inspect payload');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setInputText('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <span>Privacy & Redaction Playground</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Test PII detection, redaction, policy enforcement, and authorized restoration safely without external credentials.
          </p>
        </div>

        {/* Preset Selector */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-slate-400 font-medium">Presets:</span>
          {PRESETS.map((p) => (
            <button
              key={p.name}
              onClick={() => {
                setInputText(p.text);
                setMode(p.mode);
                setResult(null);
              }}
              className="px-2.5 py-1 text-xs rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Editor & Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Input & Settings (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Input Prompt Content
              </label>
              <button
                onClick={handleClear}
                className="text-xs text-slate-500 hover:text-slate-400 flex items-center gap-1"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear</span>
              </button>
            </div>

            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={6}
              placeholder="Paste text containing emails, phones, Indonesian NIK/NPWP, credit cards, or API secrets..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors font-mono"
            />

            {/* Controls Bar */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-slate-800/80">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Enforcement Policy Mode
                </label>
                <select
                  value={mode}
                  onChange={(e) => setMode(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="redact">Mode A: Redact (Replace PII with placeholders)</option>
                  <option value="block">Mode B: Block (Reject prohibited entities)</option>
                  <option value="allow">Mode C: Allow (Pass through permitted entities)</option>
                  <option value="redact_and_restore">Mode D: Redact & Restore (Authorized roundtrip)</option>
                  <option value="strict">Mode E: Strict Privacy (Block high-risk, redact all)</option>
                </select>
              </div>

              <div>
                <div className="flex justify-between items-center text-xs font-medium text-slate-400 mb-1">
                  <span>Confidence Threshold</span>
                  <span className="text-indigo-400 font-mono">{Math.round(minConfidence * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0.50"
                  max="1.00"
                  step="0.05"
                  value={minConfidence}
                  onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
                  className="w-full accent-indigo-500 cursor-pointer"
                />
              </div>
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={handleAnalyze}
                disabled={loading || !inputText.trim()}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg font-medium text-sm transition-colors flex items-center gap-2 shadow-lg shadow-indigo-500/20"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                <span>Evaluate & Redact</span>
              </button>
            </div>
          </div>

          {/* Detected Entities Table */}
          {result && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
              <h2 className="text-sm font-semibold text-white mb-3 flex items-center justify-between">
                <span>Detected Entities ({result.detected_entities.length})</span>
                <span className="text-xs font-normal text-slate-400">
                  {result.redaction_count} redacted
                </span>
              </h2>

              {result.detected_entities.length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-500 border border-dashed border-slate-800 rounded-lg">
                  No sensitive entities found matching the confidence threshold.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-800/60 text-slate-400 uppercase">
                      <tr>
                        <th className="py-2 px-3 rounded-l">Entity Category</th>
                        <th className="py-2 px-3">Original Detected Text</th>
                        <th className="py-2 px-3">Confidence</th>
                        <th className="py-2 px-3 rounded-r">Recognizer</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 font-mono">
                      {result.detected_entities.map((ent, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40">
                          <td className="py-2 px-3">
                            <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800 text-[11px]">
                              {ent.entity_type}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-rose-300 font-semibold">{ent.text}</td>
                          <td className="py-2 px-3 text-slate-300">
                            {Math.round(ent.confidence * 100)}%
                          </td>
                          <td className="py-2 px-3 text-slate-400">{ent.recognizer_id}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Side: Results & Outbound Preview (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {error && (
            <div className="p-4 rounded-xl border border-rose-800 bg-rose-950/40 text-rose-300 text-sm">
              {error}
            </div>
          )}

          {result ? (
            <>
              {/* Decision Badge */}
              <div
                className={`p-4 rounded-xl border ${
                  result.policy_decision === 'blocked'
                    ? 'border-rose-800/80 bg-rose-950/40'
                    : result.policy_decision === 'redacted'
                    ? 'border-indigo-800/80 bg-indigo-950/40'
                    : 'border-emerald-800/80 bg-emerald-950/40'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {result.policy_decision === 'blocked' ? (
                    <ShieldAlert className="w-5 h-5 text-rose-400" />
                  ) : (
                    <ShieldCheck className="w-5 h-5 text-emerald-400" />
                  )}
                  <span className="font-semibold text-sm capitalize text-white">
                    Policy Decision: {result.policy_decision}
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-1">{result.policy_reason}</p>
              </div>

              {/* Redacted Outbound Preview */}
              <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Outbound Upstream Payload</span>
                  </span>
                  <span className="text-[11px] text-slate-500">Sent to AI Provider</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-slate-200 whitespace-pre-wrap leading-relaxed min-h-[90px]">
                  {result.outbound_payload_preview}
                </div>
                <p className="text-[11px] text-slate-500 mt-2">
                  Upstream providers only receive collision-resistant placeholders. Raw PII never leaves your gateway.
                </p>
              </div>

              {/* Restored Simulation Preview */}
              {(mode === 'redact_and_restore' || result.restored_preview !== result.redacted_text) && (
                <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <RefreshCw className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Authorized Client Restoration</span>
                    </span>
                    <span className="text-[11px] text-emerald-400">Local-only</span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-300 whitespace-pre-wrap leading-relaxed">
                    {result.restored_preview}
                  </div>
                  <p className="text-[11px] text-slate-500 mt-2">
                    Authorized placeholders restored strictly on response return, using the request-scoped memory vault.
                  </p>
                </div>
              )}
            </>
          ) : (
            <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/30 p-8 text-center text-slate-500 text-xs flex flex-col items-center justify-center min-h-[300px]">
              <Lock className="w-8 h-8 text-slate-700 mb-2" />
              <span>Click "Evaluate & Redact" to inspect detection results, privacy policy decisions, and sanitized outbound payloads.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
