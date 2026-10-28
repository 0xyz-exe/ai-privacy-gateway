import React, { useState, useEffect } from 'react';
import {
  Shield, Sparkles, Sliders, Cpu, Key, BarChart3,
  FileText, Settings, ExternalLink, Activity
} from 'lucide-react';
import { OverviewView } from './components/OverviewView';
import { PlaygroundView } from './components/PlaygroundView';
import { PoliciesView } from './components/PoliciesView';
import { ProvidersView } from './components/ProvidersView';
import { APIKeysView } from './components/APIKeysView';
import { UsageView } from './components/UsageView';
import { AuditLogsView } from './components/AuditLogsView';
import { SettingsView } from './components/SettingsView';
import { api } from './api';
import type { ViewTab } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<ViewTab>('overview');
  const [healthStatus, setHealthStatus] = useState<string>('checking');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await api.getHealth();
        setHealthStatus(res.status === 'healthy' ? 'healthy' : 'degraded');
      } catch {
        setHealthStatus('offline');
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems: { id: ViewTab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <Activity className="w-4 h-4" /> },
    { id: 'playground', label: 'Playground', icon: <Sparkles className="w-4 h-4" /> },
    { id: 'policies', label: 'Privacy Policies', icon: <Sliders className="w-4 h-4" /> },
    { id: 'providers', label: 'AI Providers', icon: <Cpu className="w-4 h-4" /> },
    { id: 'keys', label: 'API Keys', icon: <Key className="w-4 h-4" /> },
    { id: 'usage', label: 'Usage & Costs', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'audit-logs', label: 'Audit Logs', icon: <FileText className="w-4 h-4" /> },
    { id: 'settings', label: 'Settings & Docs', icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/80 bg-slate-950 flex flex-col shrink-0">
        <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-sm text-white tracking-tight">AI Privacy Gateway</div>
            <div className="text-[11px] text-slate-500 font-mono">v1.0.0-oss</div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Footer Gateway Status */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  healthStatus === 'healthy'
                    ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]'
                    : healthStatus === 'checking'
                    ? 'bg-amber-400 animate-ping'
                    : 'bg-rose-400'
                }`}
              />
              <span className="capitalize text-slate-400 font-medium">Gateway {healthStatus}</span>
            </div>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-slate-500 hover:text-indigo-400 transition-colors flex items-center gap-1"
              title="Swagger OpenAPI Docs"
            >
              <span>API</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Console</span>
            <span>/</span>
            <span className="text-slate-200 capitalize font-medium">{activeTab.replace('-', ' ')}</span>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-400">
              <span className="text-slate-500">Proxy Target:</span>
              <span className="font-mono text-indigo-400">:8000/v1</span>
            </div>
          </div>
        </header>

        {/* View Component */}
        <main className="flex-1 p-8 overflow-y-auto">
          {activeTab === 'overview' && <OverviewView onNavigate={setActiveTab} />}
          {activeTab === 'playground' && <PlaygroundView />}
          {activeTab === 'policies' && <PoliciesView />}
          {activeTab === 'providers' && <ProvidersView />}
          {activeTab === 'keys' && <APIKeysView />}
          {activeTab === 'usage' && <UsageView />}
          {activeTab === 'audit-logs' && <AuditLogsView />}
          {activeTab === 'settings' && <SettingsView />}
        </main>
      </div>
    </div>
  );
}

export default App;
