import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { NewCasePage } from './pages/NewCasePage';
import { CaseWorkspacePage } from './pages/CaseWorkspacePage';
import { ResearchProgressPage } from './pages/ResearchProgressPage';
import { ReportViewerPage } from './pages/ReportViewerPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { api } from './services/api';

export function App() {
  const [currentView, setCurrentView] = useState<string>('dashboard');
  const [selectedCaseId, setSelectedCaseId] = useState<string>('sample-case-id');
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [selectedReportId, setSelectedReportId] = useState<string>('');
  const [currentUser, setCurrentUser] = useState<any>({
    email: 'counsel@lexintel.ai',
    full_name: 'Lead Legal Counsel',
    role: 'partner'
  });
  const [backendHealth, setBackendHealth] = useState<any>(null);

  useEffect(() => {
    // Check backend health & prefetch default case
    api.getHealth()
      .then(h => setBackendHealth(h))
      .catch(e => console.warn('Backend offline or initializing:', e));

    api.getCases()
      .then(cases => {
        if (cases.length > 0 && selectedCaseId === 'sample-case-id') {
          setSelectedCaseId(cases[0].id);
        }
      })
      .catch(e => console.warn('Error fetching cases:', e));
  }, []);

  const handleNavigate = (view: string, caseId?: string, sessionId?: string, reportId?: string) => {
    if (caseId) setSelectedCaseId(caseId);
    if (sessionId) setSelectedSessionId(sessionId);
    if (reportId) setSelectedReportId(reportId);
    setCurrentView(view);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (currentView === 'landing') {
    return <LandingPage onEnter={() => setCurrentView('dashboard')} />;
  }

  if (currentView === 'login') {
    return <LoginPage onLoginSuccess={(u) => { setCurrentUser(u); setCurrentView('dashboard'); }} />;
  }

  return (
    <div className="min-h-screen bg-[#060913] text-slate-100 flex flex-col">
      <Navbar currentView={currentView} onNavigate={handleNavigate} user={currentUser} />

      <div className="flex-1 flex max-w-[1600px] w-full mx-auto">
        <Sidebar currentView={currentView} onNavigate={handleNavigate} />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          {currentView === 'dashboard' && (
            <DashboardPage onNavigate={handleNavigate} />
          )}

          {currentView === 'new-case' && (
            <NewCasePage onNavigate={handleNavigate} />
          )}

          {currentView === 'workspace' && (
            <CaseWorkspacePage caseId={selectedCaseId} onNavigate={handleNavigate} />
          )}

          {currentView === 'research-progress' && (
            <ResearchProgressPage
              caseId={selectedCaseId}
              sessionId={selectedSessionId}
              onNavigate={handleNavigate}
            />
          )}

          {currentView === 'report-viewer' && (
            <ReportViewerPage
              caseId={selectedCaseId}
              reportId={selectedReportId}
              onNavigate={handleNavigate}
            />
          )}

          {currentView === 'cases' && (
            <DashboardPage onNavigate={handleNavigate} />
          )}

          {currentView === 'evaluation' && (
            <EvaluationPage onNavigate={handleNavigate} />
          )}

          {currentView === 'knowledge' && (
            <div className="space-y-6">
              <div className="pb-4 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h1 className="text-xl font-bold text-white font-['Cinzel',serif]">Knowledge Sources & Jurisdiction Catalog</h1>
                  <p className="text-xs text-slate-400 mt-1">Pre-indexed public statutes, restatements, and landmark judicial precedents with jurisdiction metadata</p>
                </div>
                <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-500/30">
                  26 Verified Chunks Indexed
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-5 rounded-xl legal-card border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">Statutory Codes & Restatements</span>
                    <span className="text-[10px] text-blue-400 font-mono">6 Authorities</span>
                  </div>
                  <ul className="text-xs text-slate-300 space-y-2.5">
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Sarbanes-Oxley Act § 806 (18 U.S.C. § 1514A)</div>
                      <div className="text-[10px] text-slate-400">Jurisdiction: US Federal | Whistleblower protection for contractors</div>
                    </li>
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Computer Fraud & Abuse Act (18 U.S.C. § 1030)</div>
                      <div className="text-[10px] text-slate-400">Jurisdiction: US Federal | Technological access boundaries & CFAA</div>
                    </li>
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Restatement (Second) of Contracts §§ 241, 356</div>
                      <div className="text-[10px] text-slate-400">Jurisdiction: US Common Law | Material breach & liquidated damages penalty doctrine</div>
                    </li>
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Uniform Commercial Code (UCC) § 2-718</div>
                      <div className="text-[10px] text-slate-400">Jurisdiction: Commercial Law | Statutory liquidation of damages</div>
                    </li>
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Defend Trade Secrets Act (18 U.S.C. § 1836) & UTSA</div>
                      <div className="text-[10px] text-slate-400">Jurisdiction: US Federal / Uniform State | Trade secret misappropriation</div>
                    </li>
                  </ul>
                </div>

                <div className="p-5 rounded-xl legal-card border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">Landmark Judicial Precedents</span>
                    <span className="text-[10px] text-indigo-400 font-mono">5 Authorities</span>
                  </div>
                  <ul className="text-xs text-slate-300 space-y-2.5">
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Lawson v. FMR LLC, 571 U.S. 429 (2014)</div>
                      <div className="text-[10px] text-slate-400">Court: US Supreme Court | Standing for contractor employees under SOX § 806</div>
                    </li>
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Van Buren v. United States, 593 U.S. 374 (2021)</div>
                      <div className="text-[10px] text-slate-400">Court: US Supreme Court | Gates-up technological model for CFAA access</div>
                    </li>
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Hadley v. Baxendale, 9 Exch. 341 (1854)</div>
                      <div className="text-[10px] text-slate-400">Court: Court of Exchequer | Foreseeability of consequential lost commercial profits</div>
                    </li>
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Campbell v. Acuff-Rose Music, 510 U.S. 569 (1994)</div>
                      <div className="text-[10px] text-slate-400">Court: US Supreme Court | Transformative parody & commercial fair use</div>
                    </li>
                    <li className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div className="font-semibold text-white">Digital Realty Trust, Inc. v. Somers, 583 U.S. 149 (2018)</div>
                      <div className="text-[10px] text-slate-400">Court: US Supreme Court | External SEC reporting definitions</div>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-blue-950/30 border border-blue-500/20 text-xs text-slate-300">
                <strong className="text-blue-400 block mb-1">Jurisdiction Specificity Notice:</strong>
                Legal applicability depends strictly on the governing jurisdiction. The benchmark legal corpus currently models United States Federal and Commercial Common Law frameworks. Expanding to additional jurisdictions (UK Common Law, EU, etc.) is supported natively by the metadata schema.
              </div>
            </div>
          )}

          {currentView === 'architecture' && (
            <div className="space-y-6">
              <div className="pb-4 border-b border-slate-800">
                <h1 className="text-xl font-bold text-white font-['Cinzel',serif]">LangGraph Multi-Agent Architecture</h1>
                <p className="text-xs text-slate-400 mt-1">Four-Agent LangGraph with Adaptive Agentic RAG, Adversarial Self-Play & Dynamic Evaluation</p>
              </div>
              <div className="p-6 rounded-xl legal-card border border-slate-800 text-xs text-slate-300 space-y-4">
                <div className="font-mono bg-slate-950 p-4 rounded-lg leading-relaxed text-blue-300 overflow-x-auto">
                  CaseIntakeAgent — Facts, Issues & Evidence Audit<br />
                  &nbsp;&nbsp;↓<br />
                  LegalResearchAgent — Adaptive Agentic RAG & Authority Verification<br />
                  &nbsp;&nbsp;↓<br />
                  AdvocateAgent — Defender ↔ Attacker Courtroom Stress Test<br />
                  &nbsp;&nbsp;↓<br />
                  AdjudicatorReportingAgent — Merits, Citation, Root-Cause & Report<br />
                  &nbsp;&nbsp;↓<br />
                  Dynamic Quality Gate<br />
                  &nbsp;&nbsp;├─ PASS → Final Dossier + Per-Run Evaluation Metrics<br />
                  &nbsp;&nbsp;└─ REVISE → Targeted upstream agent → Adjudicator<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ unresolved after budget → INCONCLUSIVE
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
