import React, { useEffect, useState } from 'react';
import { Key, Plus, Copy, Check, AlertCircle } from 'lucide-react';
import { api } from '../api';
import type { APIKeyItem, PrivacyPolicy } from '../types';

export const APIKeysView: React.FC = () => {
  const [keys, setKeys] = useState<APIKeyItem[]>([]);
  const [policies, setPolicies] = useState<PrivacyPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newKeySecret, setNewKeySecret] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form
  const [name, setName] = useState('');
  const [policyId, setPolicyId] = useState<number | undefined>(undefined);
  const [rateLimit, setRateLimit] = useState(60);

  const fetchKeys = async () => {
    try {
      const [keysData, polsData] = await Promise.all([
        api.getKeys(),
        api.getPolicies(),
      ]);
      setKeys(keysData);
      setPolicies(polsData);
    } catch (e: any) {
      setError(e.message || 'Failed to load keys');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await api.createKey({
        name,
        policy_id: policyId,
        rate_limit: rateLimit,
      });
      setNewKeySecret(res.raw_key);
      setName('');
      fetchKeys();
    } catch (e: any) {
      setError(e.message || 'Failed to generate key');
    }
  };

  const handleCopy = () => {
    if (newKeySecret) {
      navigator.clipboard.writeText(newKeySecret);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRevoke = async (id: number) => {
    if (!confirm('Revoking will immediately block any requests using this key. Proceed?')) return;
    try {
      await api.revokeKey(id);
      fetchKeys();
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Key className="w-5 h-5 text-indigo-400" />
            <span>Gateway API Keys</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Generate client access keys to authenticate OpenAI-compatible requests at <code className="text-indigo-300 font-mono">/v1/chat/completions</code>.
          </p>
        </div>
        <button
          onClick={() => {
            setShowModal(true);
            setNewKeySecret(null);
          }}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium flex items-center gap-1.5 shadow-lg shadow-indigo-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>Generate New Key</span>
        </button>
      </div>

      {error && (
        <div className="p-3 bg-rose-950/60 border border-rose-800 rounded-lg text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-slate-500 text-sm">Loading keys...</div>
      ) : (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/60 text-xs text-slate-400 uppercase">
                <tr>
                  <th className="py-3 px-4">Key Label</th>
                  <th className="py-3 px-4">Key Prefix</th>
                  <th className="py-3 px-4">Rate Limit</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created At</th>
                  <th className="py-3 px-4">Last Used</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {keys.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-xs text-slate-500">
                      No API keys created yet. Generate your first gateway key.
                    </td>
                  </tr>
                ) : (
                  keys.map((k) => (
                    <tr key={k.id} className="hover:bg-slate-800/30">
                      <td className="py-3 px-4 font-medium text-white">{k.name}</td>
                      <td className="py-3 px-4 font-mono text-xs text-slate-300">{k.prefix}</td>
                      <td className="py-3 px-4 text-xs text-slate-400">{k.rate_limit} req/min</td>
                      <td className="py-3 px-4">
                        <span
                          className={`text-xs px-2 py-0.5 rounded font-medium border ${
                            k.is_active
                              ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                              : 'bg-rose-950/80 text-rose-300 border-rose-800'
                          }`}
                        >
                          {k.is_active ? 'Active' : 'Revoked'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-400">
                        {new Date(k.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-400">
                        {k.last_used_at ? new Date(k.last_used_at).toLocaleDateString() : 'Never'}
                      </td>
                      <td className="py-3 px-4 text-right">
                        {k.is_active && (
                          <button
                            onClick={() => handleRevoke(k.id)}
                            className="text-xs text-rose-400 hover:text-rose-300 px-2 py-1 rounded bg-rose-950/40 border border-rose-900/60 transition-colors"
                          >
                            Revoke
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Generate Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="text-lg font-bold text-white mb-2">Generate Gateway API Key</h2>

            {newKeySecret ? (
              <div className="space-y-4">
                <div className="p-3 bg-amber-950/60 border border-amber-800 rounded-lg text-xs text-amber-300">
                  Save this key now. It is shown only once and cannot be retrieved again!
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Raw API Key</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      readOnly
                      value={newKeySecret}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-indigo-300 font-mono"
                    />
                    <button
                      onClick={handleCopy}
                      className="p-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
                    >
                      {copied ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div className="flex justify-end pt-3 border-t border-slate-800">
                  <button
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium"
                  >
                    Done
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Key Label</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Production Backend Service"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Associated Privacy Policy</label>
                  <select
                    value={policyId || ''}
                    onChange={(e) => setPolicyId(e.target.value ? parseInt(e.target.value) : undefined)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">Default (Highest priority enabled policy)</option>
                    {policies.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.mode})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Rate Limit (req/min)</label>
                  <input
                    type="number"
                    value={rateLimit}
                    onChange={(e) => setRateLimit(parseInt(e.target.value) || 60)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
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
                    Generate Key
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
