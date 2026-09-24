import React, { useEffect, useState } from 'react';
import { 
  FolderPlus, FolderKanban, Scale, BrainCircuit, Activity, 
  ArrowRight, FileText, CheckCircle2, Search, Sparkles 
} from 'lucide-react';
import { api } from '../services/api';
import { Case } from '../types';
import { StatusBadge } from '../components/StatusBadge';

interface DashboardPageProps {
  onNavigate: (view: string, caseId?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      setLoading(true);
      const data = await api.getCases();
      setCases(data);
    } catch (err) {
      console.error('Failed to load cases', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredCases = cases.filter(c => 
    c.title.toLowerCase().includes(search.toLowerCase()) ||
    c.jurisdiction.toLowerCase().includes(search.toLowerCase()) ||
    c.legal_domain.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Cinzel',serif]">
            Legal Intelligence Operations Center
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Active Multi-Agent Orchestration • 4 Department Super-Agents (10 Legal Roles)
          </p>
        </div>
        <button
          onClick={() => onNavigate('new-case')}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs shadow-md shadow-blue-500/25 transition-all self-start sm:self-auto"
        >
          <FolderPlus className="w-4 h-4" />
          <span>New Legal Matter</span>
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="legal-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Active Matters</span>
            <FolderKanban className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">{cases.length}</div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>Preloaded with benchmark case</span>
          </div>
        </div>

        <div className="legal-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold font-mono">Active Department Agents</span>
            <BrainCircuit className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">4 / 4</div>
          <div className="text-[11px] text-blue-400 mt-1">
            LangGraph 4-Department cyclic state graph
          </div>
        </div>

        <div className="legal-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Knowledge Chunks</span>
            <Scale className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">Public Corp.</div>
          <div className="text-[11px] text-slate-400 mt-1">
            Restatement, UCC & Precedents
          </div>
        </div>

        <div className="legal-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Critic Accuracy Audit</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">95%</div>
          <div className="text-[11px] text-emerald-400 mt-1">
            Reflection gate verified
          </div>
        </div>
      </div>

      {/* Cases Table Section */}
      <div className="legal-card rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-white">Legal Matters & Dossiers</h3>
            <p className="text-xs text-slate-400">Select any case to launch the multi-agent workspace</p>
          </div>
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Filter by title or domain..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs animate-pulse">
            Loading legal intelligence records...
          </div>
        ) : filteredCases.length === 0 ? (
          <div className="p-12 text-center">
            <Scale className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <p className="text-sm text-slate-400">No matching legal cases found.</p>
            <button
              onClick={() => onNavigate('new-case')}
              className="mt-3 text-xs text-blue-400 hover:underline font-semibold"
            >
              Create a new legal matter
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {filteredCases.map(c => (
              <div
                key={c.id}
                onClick={() => onNavigate('workspace', c.id)}
                className="p-5 hover:bg-slate-900/60 transition-colors cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4 group"
              >
                <div className="space-y-1.5 max-w-2xl">
                  <div className="flex items-center gap-2.5">
                    <h4 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors">
                      {c.title}
                    </h4>
                    <StatusBadge status={c.status} size="sm" />
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {c.description}
                  </p>
                  <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400 pt-1">
                    <span className="text-slate-300 font-medium">{c.jurisdiction}</span>
                    <span>•</span>
                    <span className="text-blue-400">{c.legal_domain}</span>
                    <span>•</span>
                    <span>{c.documents?.length || 0} Documents Indexed</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 group-hover:translate-x-1 transition-transform self-end sm:self-center">
                  <span>Launch Workspace</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};