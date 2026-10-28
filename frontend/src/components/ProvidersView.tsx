import React, { useEffect, useState } from 'react';
import { Cpu, Plus, Trash2, RefreshCw, Zap } from 'lucide-react';
import { api } from '../api';
import type { ProviderItem } from '../types';

export const ProvidersView: React.FC = () => {
  const [providers, setProviders] = useState<ProviderItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [testingId, setTestingId] = useState<number | null>(null);
  const [testResults, setTestResults] = useState<Record<number, { status: string; message: string }>>({});
  const [error, setError] = useState<string | null>(null);

  // Form
  const [name, setName] = useState('');
  const [providerType, setProviderType] = useState<'openai' | 'ollama' | 'mock'>('openai');
  const [baseUrl, setBaseUrl] = useState('https://api.openai.com/v1');
  const [apiKey, setApiKey] = useState('');
  const [timeoutSeconds, setTimeoutSeconds] = useState(60);
  const [modelsInput, setModelsInput] = useState('gpt-4o, gpt-4o-mini');

  const fetchProviders = async () => {
    try {
      const data = await api.getProviders();
      setProviders(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load providers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  const handleTest = async (id: number) => {
    setTestingId(id);
    try {
      const res = await api.testProvider(id);
      setTestResults(prev => ({ ...prev, [id]: res }));
    } catch (e: any) {
      setTestResults(prev => ({ ...prev, [id]: { status: 'error', message: e.message } }));
    } finally {
      setTestingId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.createProvider({
        name,
        provider_type: providerType,
        base_url: baseUrl,
        api_key: apiKey,
        timeout_seconds: timeoutSeconds,
        models: modelsInput.split(',').map(m => m.trim()).filter(Boolean),
        is_active: true,
      });
      setShowModal(false);
      setName('');
      setApiKey('');
      fetchProviders();
    } catch (e: any) {
      setError(e.message || 'Failed to create provider');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this provider?')) return;
    try {
      await api.deleteProvider(id);
      fetchProviders();
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <span>AI Providers & Adapters</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure upstream AI inference destinations. Credentials stay encrypted server-side and are never exposed to clients.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium flex items-center gap-1.5 shadow-lg shadow-indigo-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>Add Provider</span>
        </button>
      </div>

      {error && (
        <div className="p-3 bg-rose-950/60 border border-rose-800 rounded-lg text-xs text-rose-300">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-slate-500 text-sm">Loading providers...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {providers.map((p) => {
            const test = testResults[p.id];
            return (
              <div
                key={p.id}
                className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 flex flex-col justify-between hover:border-slate-700 transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 uppercase">
                      {p.provider_type}
                    </span>
                    {p.is_default && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                        Default
                      </span>
                    )}
                  </div>

                  <h2 className="text-base font-semibold text-white mb-1">{p.name}</h2>
                  <p className="text-xs text-slate-400 font-mono break-all mb-3">{p.base_url}</p>

                  <div className="space-y-1.5 text-xs text-slate-400 pt-3 border-t border-slate-800/80">
                    <div className="flex justify-between">
                      <span>API Key:</span>
                      <span className="font-mono text-slate-300">{p.api_key_masked || 'None (Local/Mock)'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Timeout:</span>
                      <span className="text-slate-300">{p.timeout_seconds}s</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Supported Models:</span>
                      <span className="text-slate-300 truncate max-w-[140px] text-right">
                        {p.models?.join(', ') || 'Any'}
                      </span>
                    </div>
                  </div>

                  {test && (
                    <div
                      className={`mt-3 p-2 rounded text-xs border ${
                        test.status === 'success'
                          ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300'
                          : test.status === 'warning'
                          ? 'bg-amber-950/60 border-amber-800 text-amber-300'
                          : 'bg-rose-950/60 border-rose-800 text-rose-300'
                      }`}
                    >
                      {test.message}
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                  <button
                    onClick={() => handleTest(p.id)}
                    disabled={testingId === p.id}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded border border-slate-700 flex items-center gap-1.5 transition-colors"
                  >
                    {testingId === p.id ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Zap className="w-3.5 h-3.5" />
                    )}
                    <span>Test Connection</span>
                  </button>

                  {!p.is_default && (
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-lg shadow-2xl">
            <h2 className="text-lg font-bold text-white mb-4">Add AI Provider</h2>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Provider Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Together AI / Groq / OpenAI"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Type</label>
                  <select
                    value={providerType}
                    onChange={(e: any) => {
                      setProviderType(e.target.value);
                      if (e.target.value === 'ollama') setBaseUrl('http://localhost:11434');
                      if (e.target.value === 'openai') setBaseUrl('https://api.openai.com/v1');
                    }}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="openai">OpenAI Compatible (HTTP)</option>
                    <option value="ollama">Ollama (Local)</option>
                    <option value="mock">Mock Engine (Testing)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Timeout (seconds)</label>
                  <input
                    type="number"
                    value={timeoutSeconds}
                    onChange={(e) => setTimeoutSeconds(parseInt(e.target.value) || 60)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Base Endpoint URL</label>
                <input
                  type="url"
                  required
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  placeholder="https://api.openai.com/v1"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500"
                />
                <span className="text-[10px] text-slate-500 mt-1 block">
                  SSRF protected: loopback, AWS metadata (169.254.169.254), and private IPs are blocked for remote endpoints.
                </span>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  API Key Secret (Stored encrypted server-side)
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Configured Models (comma-separated)</label>
                <input
                  type="text"
                  value={modelsInput}
                  onChange={(e) => setModelsInput(e.target.value)}
                  placeholder="gpt-4o, gpt-4o-mini"
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
                  Save Provider
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
