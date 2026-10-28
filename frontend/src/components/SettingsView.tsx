import React, { useEffect, useState } from 'react';
import { Settings, Shield, Terminal, Key, Check } from 'lucide-react';
import { api, getAdminToken, setAdminToken } from '../api';

export const SettingsView: React.FC = () => {
  const [settingsData, setSettingsData] = useState<any>(null);
  const [adminToken, setLocalAdminToken] = useState(getAdminToken());
  const [savedTokenNotice, setSavedTokenNotice] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const data = await api.getSettings();
        setSettingsData(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleSaveToken = (e: React.FormEvent) => {
    e.preventDefault();
    setAdminToken(adminToken);
    setSavedTokenNotice(true);
    setTimeout(() => setSavedTokenNotice(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Settings className="w-5 h-5 text-indigo-400" />
          <span>Gateway Settings & Quickstart</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Inspect active privacy recognizers, configure your dashboard admin token, and integrate client applications.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Admin Token & Config */}
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <h2 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
              <Key className="w-4 h-4 text-indigo-400" />
              <span>Admin Token Authentication</span>
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              Enter the admin token configured in your backend environment (<code className="text-indigo-300">GATEWAY_ADMIN_TOKEN</code>).
            </p>

            <form onSubmit={handleSaveToken} className="space-y-3">
              <div>
                <input
                  type="text"
                  value={adminToken}
                  onChange={(e) => setLocalAdminToken(e.target.value)}
                  placeholder="admin-secret-token-demo"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="flex items-center justify-between">
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors"
                >
                  Save Token
                </button>
                {savedTokenNotice && (
                  <span className="text-xs text-emerald-400 flex items-center gap-1">
                    <Check className="w-3.5 h-3.5" />
                    <span>Saved to local storage</span>
                  </span>
                )}
              </div>
            </form>
          </div>

          {/* Active Recognizers */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span>Active PII Recognizers ({settingsData?.active_recognizers?.length || 0})</span>
            </h2>

            {loading ? (
              <div className="text-xs text-slate-500">Loading recognizers...</div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                {settingsData?.active_recognizers?.map((r: any, idx: number) => (
                  <div key={idx} className="p-2 rounded bg-slate-950 border border-slate-800/80 text-xs">
                    <div className="font-semibold text-slate-200">{r.name}</div>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {r.entity_types.map((et: string) => (
                        <span key={et} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 font-mono border border-slate-700">
                          {et}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Integration Code Snippets */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2">
            <Terminal className="w-4 h-4 text-amber-400" />
            <span>Client Integration Examples</span>
          </h2>
          <p className="text-xs text-slate-400">
            Switch your OpenAI SDK base URL to <code className="text-indigo-300">http://localhost:8000/v1</code>.
          </p>

          <div>
            <span className="text-xs font-semibold text-slate-300 block mb-1">cURL (OpenAI Compatible)</span>
            <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto leading-relaxed">
{`curl -X POST http://localhost:8000/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_GATEWAY_API_KEY" \\
  -d '{
    "model": "mock-gpt-4o",
    "messages": [
      {"role": "user", "content": "Send bill to alice@test.com, NIK 3201011508900001"}
    ]
  }'`}
            </pre>
          </div>

          <div>
            <span className="text-xs font-semibold text-slate-300 block mb-1">Python (openai SDK)</span>
            <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto leading-relaxed">
{`from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="YOUR_GATEWAY_API_KEY"
)

response = client.chat.completions.create(
    model="mock-gpt-4o",
    messages=[
        {"role": "user", "content": "Kirim email ke budi@test.id, NIK 3201011508900001"}
    ]
)
print(response.choices[0].message.content)`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
