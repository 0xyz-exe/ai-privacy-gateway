import React, { useEffect, useState } from 'react';
import { Shield, Plus, Trash2, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../api';
import type { PrivacyPolicy } from '../types';

const COMMON_ENTITIES = [
  'EMAIL_ADDRESS', 'PHONE_NUMBER', 'CREDIT_CARD', 'IP_ADDRESS',
  'DATE_OF_BIRTH', 'PASSPORT', 'IBAN', 'NIK', 'NPWP',
  'INDONESIAN_PHONE', 'INDONESIAN_BANK_ACCOUNT', 'API_KEY', 'SECRET_KEY'
];

export const PoliciesView: React.FC = () => {
  const [policies, setPolicies] = useState<PrivacyPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [mode, setMode] = useState<'redact' | 'block' | 'allow' | 'redact_and_restore' | 'strict'>('redact');
  const [priority, setPriority] = useState(100);
  const [minConfidence, setMinConfidence] = useState(0.70);
  const [blockedEntities, setBlockedEntities] = useState<string[]>([]);
  const [responseScanning, setResponseScanning] = useState(true);
  const [streamingAllowed, setStreamingAllowed] = useState(true);

  const fetchPolicies = async () => {
    try {
      const data = await api.getPolicies();
      setPolicies(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load policies');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.createPolicy({
        name,
        description,
        mode,
        priority,
        min_confidence: minConfidence,
        blocked_entities: blockedEntities,
        allowed_entities: [],
        response_scanning: responseScanning,
        streaming_allowed: streamingAllowed,
      });
      setShowModal(false);
      setName('');
      setDescription('');
      fetchPolicies();
    } catch (e: any) {
      setError(e.message || 'Failed to create policy');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this policy?')) return;
    try {
      await api.deletePolicy(id);
      fetchPolicies();
    } catch (e: any) {
      alert(e.message || 'Failed to delete');
    }
  };

  const toggleBlockedEntity = (ent: string) => {
    if (blockedEntities.includes(ent)) {
      setBlockedEntities(blockedEntities.filter(e => e !== ent));
    } else {
      setBlockedEntities([...blockedEntities, ent]);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Shield className="w-5 h-5 text-indigo-400" />
            <span>Privacy Policies</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Define declarative privacy rules, entity categories, confidence gates, and redaction modes evaluated on every AI request.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium flex items-center gap-1.5 shadow-lg shadow-indigo-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>New Policy</span>
        </button>
      </div>

      {error && (
        <div className="p-3 bg-rose-950/60 border border-rose-800 rounded-lg text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-slate-500 text-sm">Loading policies...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {policies.map((p) => (
            <div
              key={p.id}
              className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 flex flex-col justify-between hover:border-slate-700 transition-colors"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span
                    className={`text-[11px] font-semibold px-2 py-0.5 rounded border uppercase ${
                      p.mode === 'block'
                        ? 'bg-rose-950 text-rose-300 border-rose-800'
                        : p.mode === 'redact_and_restore'
                        ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                        : p.mode === 'strict'
                        ? 'bg-amber-950 text-amber-300 border-amber-800'
                        : 'bg-indigo-950 text-indigo-300 border-indigo-800'
                    }`}
                  >
                    Mode: {p.mode.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-slate-500 font-mono">Priority: {p.priority}</span>
                </div>

                <h2 className="text-base font-semibold text-white mb-1">{p.name}</h2>
                <p className="text-xs text-slate-400 mb-3 leading-relaxed">{p.description || 'No description'}</p>

                <div className="space-y-1.5 text-xs text-slate-400 pt-3 border-t border-slate-800/80">
                  <div className="flex justify-between">
                    <span>Min Confidence:</span>
                    <span className="text-slate-200 font-mono">{Math.round(p.min_confidence * 100)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Response Scanning:</span>
                    <span className="text-slate-200">{p.response_scanning ? 'Active' : 'Disabled'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Streaming:</span>
                    <span className="text-slate-200">{p.streaming_allowed ? 'Allowed' : 'Blocked'}</span>
                  </div>
                </div>

                {p.blocked_entities && p.blocked_entities.length > 0 && (
                  <div className="mt-3">
                    <span className="text-[11px] text-slate-400 block mb-1">Blocked Entities:</span>
                    <div className="flex flex-wrap gap-1">
                      {p.blocked_entities.map((ent) => (
                        <span key={ent} className="text-[10px] px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-900 font-mono">
                          {ent}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5 text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Enabled</span>
                </div>
                <button
                  onClick={() => handleDelete(p.id)}
                  className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-lg shadow-2xl">
            <h2 className="text-lg font-bold text-white mb-4">Create New Privacy Policy</h2>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Policy Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Strict Healthcare & PII"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={2}
                  placeholder="Policy rules and enforcement goals..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Mode</label>
                  <select
                    value={mode}
                    onChange={(e: any) => setMode(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="redact">Redact (Placeholder replacement)</option>
                    <option value="block">Block (Reject violations)</option>
                    <option value="allow">Allow (Allow permitted)</option>
                    <option value="redact_and_restore">Redact & Restore (Authorized)</option>
                    <option value="strict">Strict Privacy</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Priority</label>
                  <input
                    type="number"
                    value={priority}
                    onChange={(e) => setPriority(parseInt(e.target.value) || 100)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center text-xs font-medium text-slate-300 mb-1">
                  <span>Minimum Detection Confidence</span>
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

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Prohibited Entities (Click to toggle)</label>
                <div className="flex flex-wrap gap-1.5 p-2 bg-slate-950 border border-slate-800 rounded-lg max-h-28 overflow-y-auto">
                  {COMMON_ENTITIES.map((ent) => {
                    const selected = blockedEntities.includes(ent);
                    return (
                      <button
                        type="button"
                        key={ent}
                        onClick={() => toggleBlockedEntity(ent)}
                        className={`text-[10px] px-2 py-0.5 rounded font-mono border transition-colors ${
                          selected
                            ? 'bg-rose-950 text-rose-300 border-rose-800'
                            : 'bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-600'
                        }`}
                      >
                        {ent}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-300 pt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={responseScanning}
                    onChange={(e) => setResponseScanning(e.target.checked)}
                    className="accent-indigo-500"
                  />
                  <span>Scan AI responses for PII</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={streamingAllowed}
                    onChange={(e) => setStreamingAllowed(e.target.checked)}
                    className="accent-indigo-500"
                  />
                  <span>Allow Streaming</span>
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium"
                >
                  Save Policy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
