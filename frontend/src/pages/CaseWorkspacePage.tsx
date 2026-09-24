import React, { useEffect, useState } from 'react';
import { 
  ArrowLeft, Upload, FileText, Play, AlertCircle, BrainCircuit
} from 'lucide-react';
import { api } from '../services/api';
import { Case } from '../types';
import { StatusBadge } from '../components/StatusBadge';

interface CaseWorkspacePageProps {
  caseId: string;
  onNavigate: (view: string, caseId?: string, sessionId?: string, reportId?: string) => void;
}

export const CaseWorkspacePage: React.FC<CaseWorkspacePageProps> = ({ caseId, onNavigate }) => {
  const [caseItem, setCaseItem] = useState<Case | null>(null);
  const [objective, setObjective] = useState('');
  const [executionStrategy] = useState<'full_litigation'>('full_litigation');
  const [pastSessions, setPastSessions] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const SCENARIO_PRESETS = [
    {
      label: 'Women Safety & Workplace Protection (POSH / Vishaka)',
      domain: 'Workplace Safety',
      text: 'Evaluate employer liability for failure to provide mandatory workplace safety protocols and valid Internal Complaints Committee (ICC) mechanisms. Assess whether the termination constitutes unlawful retaliatory discharge for reporting safety violations, analyze statutory compliance under workplace safety legislations and Vishaka / POSH standards, and simulate opposing counsel defenses regarding performance-based termination.'
    },
    {
      label: 'Whistleblower (SOX / Lawson)',
      domain: 'Whistleblower',
      text: 'Evaluate whether Sarbanes-Oxley § 1514A protects contractor employees from retaliatory termination under Lawson v. FMR LLC, and assess contributing factor causation.'
    },
    {
      label: 'Cyber Misuse (CFAA / Van Buren)',
      domain: 'Cyber Law',
      text: 'Analyze whether an employee accessing corporate repositories with authorized credentials can be liable under CFAA § 1030(a)(2) in light of Van Buren v. United States, and assess trade secret pivots.'
    },
    {
      label: 'Contract Penalty (Restatement § 356)',
      domain: 'Contracts',
      text: 'Analyze whether the liquidated damages clause of $5,000/day per delayed linehaul truck constitutes an unenforceable penalty under Restatement (Second) of Contracts § 356, and evaluate exposure to $350,000 in claimed lost goodwill under Hadley v. Baxendale.'
    }
  ];

  useEffect(() => {
    loadCase();
    loadSessions();
  }, [caseId]);

  const loadCase = async () => {
    try {
      const data = await api.getCase(caseId);
      setCaseItem(data);
      if (!objective) {
        // Dynamic LLM objective derivation from case factual description or domain
        if (data.description && data.description.trim().length > 10) {
          setObjective(`Analyze statutory compliance, employer/defendant liability, evidentiary support, and opposing counsel defenses for the following matter: ${data.description}`);
        } else {
          const domain = (data.legal_domain || '').toLowerCase();
          const title = (data.title || '').toLowerCase();
          if (domain.includes('women') || domain.includes('safety') || domain.includes('harassment') || title.includes('women')) {
            setObjective(SCENARIO_PRESETS[0].text);
          } else if (domain.includes('whistleblower')) {
            setObjective(SCENARIO_PRESETS[1].text);
          } else if (domain.includes('cyber') || domain.includes('tech')) {
            setObjective(SCENARIO_PRESETS[2].text);
          } else {
            setObjective(SCENARIO_PRESETS[0].text);
          }
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load case');
    }
  };

  const loadSessions = async () => {
    try {
      const sessions = await api.getCaseSessions(caseId);
      setPastSessions(sessions);
    } catch {
      // Non-blocking
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploading(true);
    setError(null);
    try {
      await api.uploadDocument(caseId, file);
      await loadCase();
    } catch (err: any) {
      setError(err.message || 'File upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleStartAnalysis = async () => {
    if (!objective.trim()) {
      setError('Please provide a strategic legal question or research objective.');
      return;
    }
    setStarting(true);
    setError(null);
    try {
      const session = await api.startResearch(caseId, objective, executionStrategy);
      onNavigate('research-progress', caseId, session.id);
    } catch (err: any) {
      setError(err.message || 'Failed to initiate multi-agent analysis');
      setStarting(false);
    }
  };

  if (!caseItem) {
    return (
      <div className="p-12 text-center text-slate-400 text-xs animate-pulse">
        Loading legal matter workspace...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('dashboard')}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white font-['Cinzel',serif]">{caseItem.title}</h1>
              <StatusBadge status={caseItem.status} size="sm" />
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
              <span>{caseItem.jurisdiction}</span>
              <span>•</span>
              <span className="text-blue-400 font-medium">{caseItem.legal_domain}</span>
              {caseItem.client_name && (
                <>
                  <span>•</span>
                  <span>Client: {caseItem.client_name}</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-lg bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Grid: Facts & Strategic Question */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Facts & Strategic Question */}
        <div className="lg:col-span-2 space-y-6">
          <div className="legal-card p-6 rounded-xl border border-slate-800">
            <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" />
              <span>Factual Record & Procedural History</span>
            </h3>
            <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800/80 text-xs text-slate-300 leading-relaxed max-h-48 overflow-y-auto">
              {caseItem.description}
            </div>
          </div>

          <div className="legal-card p-6 rounded-xl border border-blue-500/30 shadow-lg shadow-blue-500/5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <BrainCircuit className="w-4 h-4 text-blue-400" />
                  <span>Strategic Legal Question / Objective</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Define the primary inquiry or select a benchmark scenario below.
                </p>
              </div>
              <span className="text-[10px] text-blue-400 font-mono px-2 py-0.5 rounded bg-blue-950/60 border border-blue-800/40 self-start sm:self-auto">
                Autonomous Routing Enabled
              </span>
            </div>

            {/* Quick Scenario Selectors */}
            <div className="space-y-1.5">
              <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase block">
                Scenario Quick-Select Presets:
              </span>
              <div className="flex flex-wrap gap-2">
                {SCENARIO_PRESETS.map((sc, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setObjective(sc.text)}
                    className="px-2.5 py-1 rounded bg-slate-900 hover:bg-blue-900/40 text-slate-300 hover:text-blue-200 border border-slate-800 hover:border-blue-700/60 text-[11px] font-medium transition-all"
                  >
                    {sc.label}
                  </button>
                ))}
              </div>
            </div>

            <textarea
              value={objective}
              onChange={e => setObjective(e.target.value)}
              rows={4}
              placeholder="e.g. Assess liability, evaluate penalty doctrine, and simulate opposing counsel defenses..."
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-blue-500 leading-relaxed font-sans"
            />

            <div className="p-3 rounded-lg bg-slate-950/90 border border-slate-800">
              <span className="text-xs font-bold text-white block">Execution: Full Litigation</span>
              <span className="text-[10px] text-slate-400">All four agents participate. Adaptive research, adversarial courtroom stress-test, adjudication, and dynamic per-run evaluation.</span>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
              <div className="text-[11px] text-slate-400">
                Includes adaptive Agentic RAG, courtroom stress-test, quality gate & dynamic evaluation
              </div>
              <button
                onClick={handleStartAnalysis}
                disabled={starting}
                className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2 disabled:opacity-50"
              >
                {starting ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Deliberating...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-white" />
                    <span>Start Strategic Multi-Agent Analysis</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Past Research Sessions / Memory Tab */}
          {pastSessions.length > 0 && (
            <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  <span>Prior Case Research Sessions & Memory Snapshots ({pastSessions.length})</span>
                </h3>
                <span className="text-[10px] text-emerald-400 font-mono">Cross-Turn Continuity Active</span>
              </div>
              <div className="space-y-2 max-h-56 overflow-y-auto">
                {pastSessions.map((s, idx) => (
                  <div key={s.id || idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 flex items-center justify-between text-xs gap-3">
                    <div className="truncate">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                          {s.status?.toUpperCase()}
                        </span>
                        {s.iteration_count > 0 && (
                          <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/40">
                            {s.iteration_count} Revisions
                          </span>
                        )}
                        <span className="text-slate-400 text-[10px]">
                          {new Date(s.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-slate-300 truncate font-medium max-w-lg">{s.objective}</p>
                    </div>
                    {s.reports && s.reports.length > 0 && (
                      <button
                        onClick={() => onNavigate('report-view', caseId, s.id, s.reports[0].id)}
                        className="px-3 py-1 rounded bg-blue-950 hover:bg-blue-900 border border-blue-700/50 text-blue-300 hover:text-white text-xs font-semibold shrink-0 transition-colors"
                      >
                        View Dossier
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Documents & Evidence Intake */}
        <div className="space-y-6">
          <div className="legal-card p-6 rounded-xl border border-slate-800">
            <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
              <Upload className="w-4 h-4 text-blue-400" />
              <span>Evidentiary Ingestion</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Upload contracts, pleadings, emails, or disclosures (PDF, TXT, MD). Chunks are indexed into the hybrid vector store.
            </p>

            <label className="border-2 border-dashed border-slate-700 hover:border-blue-500/60 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-colors bg-slate-950/40">
              <Upload className="w-6 h-6 text-slate-500 mb-2" />
              <span className="text-xs font-semibold text-slate-300">
                {uploading ? 'Processing & Chunking...' : 'Click to Upload Legal Document'}
              </span>
              <span className="text-[10px] text-slate-400 mt-1">PyMuPDF / Vector Indexing</span>
              <input
                type="file"
                disabled={uploading}
                onChange={handleFileUpload}
                accept=".pdf,.txt,.md,.markdown,.html"
                className="hidden"
              />
            </label>

            {/* Document list */}
            <div className="mt-4 space-y-2">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                Ingested Documents ({caseItem.documents?.length || 0})
              </span>
              {caseItem.documents?.length === 0 ? (
                <div className="text-xs text-slate-400 italic p-3 bg-slate-950/60 rounded-lg text-center">
                  No case-specific exhibits uploaded yet. Pre-loaded public statutes and precedents will be utilized.
                </div>
              ) : (
                caseItem.documents.map(doc => (
                  <div key={doc.id} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2 truncate">
                      <FileText className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                      <span className="text-white truncate font-medium">{doc.file_name}</span>
                    </div>
                    <span className="text-[10px] text-emerald-400 font-mono shrink-0 ml-2">
                      {doc.chunk_count} chunks
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};