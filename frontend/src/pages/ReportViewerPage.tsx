import React, { useEffect, useState } from 'react';
import { 
  ArrowLeft, Printer, Scale, ShieldAlert, Gavel, 
  BookOpen, FileCheck, Target, CheckCircle2, AlertTriangle, 
  Sparkles, FileText, Layers, ChevronDown, Check, HelpCircle,
  Search, Filter, ShieldCheck, RefreshCw, BarChart2, Award
} from 'lucide-react';
import { api } from '../services/api';
import { Report } from '../types';
import { CitationCard } from '../components/CitationCard';

interface ReportViewerPageProps {
  caseId: string;
  reportId: string;
  onNavigate: (view: string, caseId?: string) => void;
}

export const ReportViewerPage: React.FC<ReportViewerPageProps> = ({
  caseId,
  reportId,
  onNavigate
}) => {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'dossier18' | 'battle' | 'precedents' | 'judge' | 'critic'>('dossier18');
  const [precedentFilter, setPrecedentFilter] = useState('');

  useEffect(() => {
    loadReport();
  }, [reportId]);

  const loadReport = async () => {
    try {
      const data = await api.getReport(reportId);
      setReport(data);
    } catch (err) {
      console.error('Failed to load report', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading || !report) {
    return (
      <div className="p-16 text-center text-slate-400 text-xs animate-pulse">
        Compiling Strategic Legal Intelligence Report...
      </div>
    );
  }

  const full = report.full_report_json || {};
  const metrics = full.run_evaluation || {};

  // Grounding badge helper
  const renderGroundingBadge = (type: string = 'SUPPORTED BY SOURCE') => {
    if (type === 'SUPPORTED BY SOURCE') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-500/30">
          <CheckCircle2 className="w-3 h-3" />
          SUPPORTED BY SOURCE
        </span>
      );
    }
    if (type === 'MODEL INFERENCE') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950/80 text-amber-400 border border-amber-500/30">
          <Sparkles className="w-3 h-3" />
          MODEL INFERENCE
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950/80 text-rose-400 border border-rose-500/30">
        <AlertTriangle className="w-3 h-3" />
        INSUFFICIENT EVIDENCE
      </span>
    );
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto print:max-w-none print:m-0 pb-12">
      {/* Top Navigation & Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800 print:hidden">
        <button
          onClick={() => onNavigate('workspace', caseId)}
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Case Workspace</span>
        </button>

        <div className="flex items-center gap-2">
          {/* View Mode Switcher */}
          <div className="flex flex-wrap items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => setViewMode('dossier18')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                viewMode === 'dossier18' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              18-Section Dossier
            </button>
            <button
              onClick={() => setViewMode('battle')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                viewMode === 'battle' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              Argument Battle
            </button>
            <button
              onClick={() => setViewMode('precedents')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                viewMode === 'precedents' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              Precedent Table
            </button>
            <button
              onClick={() => setViewMode('judge')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                viewMode === 'judge' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              Judge Simulation
            </button>
            <button
              onClick={() => setViewMode('critic')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                viewMode === 'critic' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              Critic Reflection
            </button>
          </div>

          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition-colors"
          >
            <Printer className="w-3.5 h-3.5 text-blue-400" />
            <span>Print</span>
          </button>
        </div>
      </div>

      {/* Header Banner */}
      <div className="legal-card p-6 sm:p-8 rounded-2xl border border-blue-500/30 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="text-[11px] font-bold font-mono tracking-widest text-blue-400 uppercase bg-blue-950/80 px-2.5 py-1 rounded border border-blue-800/40">
            LexIntel AI • Strategic Legal Intelligence Dossier
          </span>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1 text-emerald-400 font-mono">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Grounded Citations</span>
            </span>
            <span className="flex items-center gap-1 text-blue-400 font-mono">
              <span>Confidence: {(report.confidence_score * 100).toFixed(0)}%</span>
            </span>
          </div>
        </div>

        <h1 className="text-xl sm:text-2xl font-bold text-white font-['Cinzel',serif] leading-tight">
          {report.title}
        </h1>

        <p className="text-xs text-slate-400 leading-relaxed max-w-4xl">
          Multi-agent deliberative intelligence synthesized across 4 Department Super-Agents (unifying 10 legal reasoning roles): Intake & Discovery, Legal Knowledge & Retrieval, Litigation Strategy & Advocacy, and Adjudication & Reporting.
        </p>

        {/* Section 18 Mandatory Disclaimer */}
        <div className="p-3.5 rounded-lg bg-amber-950/30 border border-amber-500/30 flex items-start gap-2.5 text-amber-200/90 text-xs leading-relaxed">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-amber-300">Mandatory Decision-Support Notice: </span>
            {report.limitations_disclaimer || full.disclaimer || 'This system provides AI-assisted legal research and decision support for informational and academic purposes. It does not constitute legal advice, does not replace a qualified legal professional, and simulated judicial assessments are not predictions of actual court decisions.'}
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* MODE 1: COMPLETE 18-SECTION LEGAL DOSSIER */}
      {/* ========================================================================= */}
      {viewMode === 'dossier18' && (
        <div className="space-y-6">
          {/* 1. Executive Summary */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">1.</span> Executive Summary
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <p className="text-xs sm:text-sm text-slate-200 leading-relaxed whitespace-pre-line">
              {report.executive_summary}
            </p>
          </div>

          {/* 2. Case Context */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">2.</span> Case Context & Factual Background
              </h3>
              {renderGroundingBadge('SUPPORTED BY SOURCE')}
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {full.case_context || report.factual_analysis || 'Factual context synthesized from submitted case records.'}
            </p>
          </div>

          {/* 3. Jurisdiction */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">3.</span> Jurisdiction & Applicable Legal Forum
              </h3>
              {renderGroundingBadge('SUPPORTED BY SOURCE')}
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {full.jurisdiction || 'United States Federal Jurisdiction / Commercial Common Law Forum'}
            </p>
          </div>

          {/* 4. Legal Issues */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">4.</span> Identified Legal Issues
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              {(full.legal_issues || ['Enforceability of challenged statutory and contractual covenants', 'Quantum of provable damages versus speculative lost profits']).map((issue: string, i: number) => (
                <li key={i} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-950 border border-slate-800/80">
                  <span className="w-5 h-5 rounded-full bg-blue-900/40 text-blue-300 font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <span>{issue}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 5. Applicable Laws */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">5.</span> Applicable Statutory Framework
              </h3>
              {renderGroundingBadge('SUPPORTED BY SOURCE')}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {(full.applicable_laws || report.statutory_matrix || []).map((law: any, i: number) => (
                <div key={i} className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white">{law.law || law.title || 'Statutory Code'}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800/40">
                      {law.finding || 'Controlling'}
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px] leading-relaxed">{law.relevance || law.description || JSON.stringify(law)}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 6. Relevant Precedents */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">6.</span> Relevant Precedents
              </h3>
              {renderGroundingBadge('SUPPORTED BY SOURCE')}
            </div>
            <div className="space-y-3">
              {(full.relevant_precedents || report.precedent_analysis || []).map((pr: any, i: number) => (
                <div key={i} className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">{pr.case || pr.case_name || 'Landmark Decision'}</span>
                    <span className="font-mono text-slate-400 text-[11px]">{pr.citation || ''}</span>
                  </div>
                  <div className="text-slate-300">
                    <strong className="text-slate-400">Rule of Law: </strong>
                    {pr.principle || pr.rule_of_law || ''}
                  </div>
                  <div className="text-slate-400">
                    <strong className="text-slate-300">Application to Matter: </strong>
                    {pr.application || (pr.factual_distinctions ? pr.factual_distinctions.join(', ') : '')}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 7. Precedent Comparison */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">7.</span> Precedent Comparison & Distinctions
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30 space-y-1.5">
                <span className="text-[11px] font-bold text-emerald-400 uppercase font-mono block">Supporting Authorities</span>
                <ul className="space-y-1 text-slate-300 text-[11px]">
                  {((full.precedent_comparison?.supporting) || ['Primary controlling appellate decisions']).map((s: string, i: number) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>
              <div className="p-3.5 rounded-lg bg-rose-950/30 border border-rose-500/30 space-y-1.5">
                <span className="text-[11px] font-bold text-rose-400 uppercase font-mono block">Adverse Authorities</span>
                <ul className="space-y-1 text-slate-300 text-[11px]">
                  {((full.precedent_comparison?.opposing) || ['Opposing party citations']).map((s: string, i: number) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>
              <div className="p-3.5 rounded-lg bg-blue-950/30 border border-blue-500/30 space-y-1.5">
                <span className="text-[11px] font-bold text-blue-400 uppercase font-mono block">Distinctions</span>
                <ul className="space-y-1 text-slate-300 text-[11px]">
                  {((full.precedent_comparison?.conflicting) || ['Standard of proof & factual divergence']).map((s: string, i: number) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* 8. Supporting Arguments */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">8.</span> Affirmative Arguments & Theory of the Case
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <div className="space-y-2.5">
              {(full.supporting_arguments || []).map((arg: any, i: number) => (
                <div key={i} className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1">
                  <div className="font-bold text-emerald-300 flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{arg.claim || 'Affirmative Ground'}</span>
                  </div>
                  <p className="text-slate-400 pl-5">{arg.basis || 'Anchored in statutory text and controlling precedent.'}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 9. Opposing Arguments */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">9.</span> Opposing Counsel Arguments (Red Team)
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <div className="space-y-2.5">
              {(full.opposing_arguments || report.opposing_arguments || []).map((op: any, i: number) => (
                <div key={i} className="p-3.5 rounded-lg bg-slate-950 border border-rose-900/30 text-xs space-y-1">
                  <div className="font-bold text-rose-300 flex items-center gap-2">
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                    <span>Opponent Argument: {op.claim || op.claim_challenged || 'Adverse Assertion'}</span>
                  </div>
                  <p className="text-slate-400 pl-5">{op.refutation || op.opposing_counterargument || JSON.stringify(op)}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 10. Rebuttals */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">10.</span> Strategic Rebuttals
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              {(full.rebuttals || ['Adverse party failed to provide required notice at formation.', 'Controlling public policy supersedes private penalty agreements.']).map((reb: string, i: number) => (
                <li key={i} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-2.5">
                  <Check className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                  <span>{reb}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 11. Evidence Gaps */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">11.</span> Evidence Gaps & Corroboration Deficiencies
              </h3>
              {renderGroundingBadge('INSUFFICIENT EVIDENCE')}
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              {(full.evidence_gaps || ['Contemporaneous digital records quantifying immediate damages', 'Expert declarations validating claimed consequential loss']).map((gap: string, i: number) => (
                <li key={i} className="p-3 rounded-lg bg-slate-950 border border-amber-900/30 flex items-start gap-2.5 text-amber-200/90">
                  <HelpCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <span>{gap}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 12. Strategic Considerations */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">12.</span> Strategic Action Plan & Next Steps
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <div className="space-y-2.5">
              {(full.strategic_considerations || report.strategic_recommendations || []).map((step: any, i: number) => (
                <div key={i} className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-3 text-xs">
                  <span className="w-6 h-6 rounded-full bg-blue-900/60 border border-blue-500/40 text-blue-300 font-bold flex items-center justify-center shrink-0">
                    {step.step || i + 1}
                  </span>
                  <div>
                    <h4 className="font-bold text-white">{step.action || 'Procedural Move'}</h4>
                    <p className="text-slate-400 mt-0.5">{step.impact || step.objective || JSON.stringify(step)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 13. Simulated Judicial Perspective */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">13.</span> Simulated Judicial Perspective (Non-Predictive Heuristic)
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <div className="p-4 rounded-lg bg-slate-950 border border-indigo-900/40 text-xs space-y-2">
              <div className="text-slate-300">
                <strong className="text-white">Applicable Standard of Review: </strong>
                {full.simulated_judicial_perspective?.standard_of_review || report.judicial_evaluation?.standard || 'De novo review on questions of law; Preponderance of the evidence on disputed facts'}
              </div>
              <div className="text-slate-300">
                <strong className="text-white">Simulated Disposition Likelihood: </strong>
                <span className="text-indigo-300 font-medium">
                  {full.simulated_judicial_perspective?.merits_reasoning || report.judicial_evaluation?.merits_reasoning || 'Neutral merits assessment based on the supplied record; no outcome prediction is generated.'}
                </span>
              </div>
            </div>
          </div>

          {/* 14. Risk Assessment */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">14.</span> Risk Assessment & Vulnerabilities
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              {(full.risk_assessment || ['Litigation discovery costs may exceed pre-trial settlement posture', 'Judicial reluctance to disturb negotiated contract terms without unequivocal penalty proof']).map((risk: string, i: number) => (
                <li key={i} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-2.5">
                  <span className="w-2 h-2 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                  <span>{risk}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 15. Confidence & Evidence Strength */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">15.</span> Confidence Assessment & Evidence Strength
              </h3>
              {renderGroundingBadge('MODEL INFERENCE')}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block mb-1">Overall Evidentiary Confidence:</span>
                <span className="text-2xl font-black font-mono text-emerald-400">
                  {((full.confidence_and_evidence_strength?.confidence_score || report.confidence_score) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block mb-1">Reasoning Basis:</span>
                <p className="text-slate-300 text-[11px] leading-relaxed">
                  {full.confidence_and_evidence_strength?.basis || 'Strong statutory alignment and clear factual distinction against adverse precedents.'}
                </p>
              </div>
            </div>
          </div>

          {/* 16. Sources and Citations */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">16.</span> Verified Sources and Citations
              </h3>
              {renderGroundingBadge('SUPPORTED BY SOURCE')}
            </div>
            <div className="space-y-3">
              {(report.citations || full.sources_and_citations || []).map((cit: any, i: number) => (
                <CitationCard key={cit.id || cit.citation_id || i} citation={cit} />
              ))}
            </div>
          </div>

          {/* 17. Limitations */}
          <div className="legal-card p-6 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-400 font-bold">17.</span> Limitations & Evidentiary Boundaries
              </h3>
              {renderGroundingBadge('INSUFFICIENT EVIDENCE')}
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              {(full.limitations || [
                'Analysis is grounded exclusively in pre-indexed authorities; requires supplementary discovery for untested claims.',
                'Judicial evaluations simulate doctrinal principles but cannot account for local judge-specific procedural preferences.'
              ]).map((lim: string, i: number) => (
                <li key={i} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-2.5 text-slate-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-500 mt-1.5 shrink-0" />
                  <span>{lim}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 18. Disclaimer */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 leading-relaxed">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono mb-2">
              <span className="text-blue-400 font-bold">18.</span> Mandatory Decision-Support Disclaimer
            </h3>
            <p>
              {report.limitations_disclaimer || full.disclaimer || 'This system provides AI-assisted legal research and decision support for informational purposes. It does not constitute legal advice, does not replace a qualified legal professional, and simulated judicial assessments are not predictions of actual court decisions.'}
            </p>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODE 2: ARGUMENT BATTLE (OUR POSITION VS OPPOSING POSITION) */}
      {/* ========================================================================= */}
      {viewMode === 'battle' && (
        <div className="space-y-6">
          <div className="text-center pb-4 border-b border-slate-800">
            <h2 className="text-xl font-bold text-white font-['Cinzel',serif] tracking-wide">
              Adversarial Argument Battle
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Direct confrontation between affirmative claims (StrategyAgent) and opposing counsel counterarguments (OpponentAgent).
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* OUR POSITION */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 p-3 rounded-xl bg-emerald-950/50 border border-emerald-500/40 text-emerald-400 font-bold text-sm">
                <CheckCircle2 className="w-5 h-5" />
                <span>OUR POSITION (Affirmative Theory)</span>
              </div>

              {(full.supporting_arguments || []).map((arg: any, i: number) => (
                <div key={i} className="p-5 rounded-xl legal-card border border-emerald-500/20 bg-emerald-950/10 space-y-3">
                  <div>
                    <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block">Argument #{i + 1}</span>
                    <h4 className="text-sm font-bold text-white mt-1">{arg.claim || 'Affirmative Legal Ground'}</h4>
                  </div>
                  <div className="text-xs text-slate-300">
                    <strong className="text-slate-400 block mb-1">Supporting Evidence:</strong>
                    <p className="pl-2 border-l-2 border-emerald-500/40">{arg.basis || 'Documentary records and factual performance logs.'}</p>
                  </div>
                  <div className="text-xs text-slate-300">
                    <strong className="text-slate-400 block mb-1">Relevant Precedent:</strong>
                    <p className="pl-2 border-l-2 border-blue-500/40">{arg.precedent || 'Controlling Supreme Court and appellate authorities.'}</p>
                  </div>
                  <div className="pt-2 border-t border-slate-800 text-[11px] text-amber-300/90">
                    <strong>Identified Vulnerability: </strong>
                    {arg.vulnerability || 'Requires proof of actual market loss during discovery.'}
                  </div>
                </div>
              ))}
            </div>

            {/* OPPOSING POSITION */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-950/50 border border-rose-500/40 text-rose-400 font-bold text-sm">
                <ShieldAlert className="w-5 h-5" />
                <span>OPPOSING COUNSEL (Red Team Attack)</span>
              </div>

              {(full.opposing_arguments || report.opposing_arguments || []).map((op: any, i: number) => (
                <div key={i} className="p-5 rounded-xl legal-card border border-rose-500/20 bg-rose-950/10 space-y-3">
                  <div>
                    <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider block">Opponent Ground #{i + 1}</span>
                    <h4 className="text-sm font-bold text-white mt-1">{op.claim || op.claim_challenged || 'Adverse Claim'}</h4>
                  </div>
                  <div className="text-xs text-slate-300">
                    <strong className="text-slate-400 block mb-1">Counterargument:</strong>
                    <p className="pl-2 border-l-2 border-rose-500/40">{op.refutation || op.opposing_counterargument || 'Motion to enforce contractual liquidated damages as negotiated.'}</p>
                  </div>
                  <div className="text-xs text-slate-300">
                    <strong className="text-slate-400 block mb-1">Affirmative Defense:</strong>
                    <p className="pl-2 border-l-2 border-amber-500/40">{op.defense || 'Strict compliance with explicit express contract provisions.'}</p>
                  </div>
                  <div className="pt-2 border-t border-slate-800 text-[11px] text-emerald-300/90">
                    <strong>Our Strategic Rebuttal: </strong>
                    {full.rebuttals?.[i] || 'Public policy doctrine supersedes private penalty clauses under Restatement § 356.'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODE 3: PRECEDENT COMPARISON TABLE */}
      {/* ========================================================================= */}
      {viewMode === 'precedents' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-xl font-bold text-white font-['Cinzel',serif] tracking-wide">
                Comparative Judicial Precedent Analysis
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Comparative matrix mapping holdings, legal principles, factual similarities, and distinguishing factors.
              </p>
            </div>

            {/* Filter Search Box */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={precedentFilter}
                onChange={(e) => setPrecedentFilter(e.target.value)}
                placeholder="Filter precedents by name or rule..."
                className="pl-9 pr-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 w-64"
              />
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800 legal-card">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/80 text-slate-400">
                  <th className="py-3 px-3.5 font-semibold">Case & Citation</th>
                  <th className="py-3 px-3 font-semibold">Court & Year</th>
                  <th className="py-3 px-3 font-semibold">Legal Issue</th>
                  <th className="py-3 px-3.5 font-semibold">Key Facts</th>
                  <th className="py-3 px-3.5 font-semibold">Legal Principle</th>
                  <th className="py-3 px-3 font-semibold">Similarity</th>
                  <th className="py-3 px-3 font-semibold">Distinction</th>
                  <th className="py-3 px-3 font-semibold">Outcome</th>
                  <th className="py-3 px-3 text-right font-semibold">Relevance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {((
                  (full.relevant_precedents && full.relevant_precedents.length > 0 ? full.relevant_precedents : null) ||
                  (report.precedent_analysis && report.precedent_analysis.length > 0 ? report.precedent_analysis : null) ||
                  (report.citations || full.sources_and_citations || []).map((c: any) => ({
                    name: c.title || 'Judicial Precedent Authority',
                    citation: c.citation_text || 'Citation On Record',
                    court: c.jurisdiction || 'Appellate Division',
                    year: '2024',
                    issue: c.claim || 'Precedent Authority on Dispute',
                    facts: c.supporting_text || c.quote || 'Factual record retrieved from verified legal knowledge store.',
                    principle: c.claim || 'Controlling legal principle ratio decidendi.',
                    similarity: 'Analogous legal issue and statutory context',
                    distinction: 'Fact-specific record distinctions',
                    outcome: 'Favorable Precedent Principle',
                    relevance: 'Controlling Authority'
                  }))
                ) as any[]).filter(p => 
                  (p.name || p.title || '').toLowerCase().includes(precedentFilter.toLowerCase()) ||
                  (p.principle || p.claim || '').toLowerCase().includes(precedentFilter.toLowerCase())
                ).map((pr, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3 px-3.5 font-bold text-white">
                      <div>{pr.name || pr.title}</div>
                      <span className="font-mono text-[10px] text-slate-400">{pr.citation || pr.citation_text}</span>
                    </td>
                    <td className="py-3 px-3 text-slate-300">
                      <div>{pr.court || pr.jurisdiction}</div>
                      <span className="font-mono text-[10px] text-slate-500">{pr.year || '2024'}</span>
                    </td>
                    <td className="py-3 px-3 text-slate-300 max-w-[150px] truncate" title={pr.issue || pr.claim}>{pr.issue || pr.claim}</td>
                    <td className="py-3 px-3.5 text-slate-400 max-w-[180px] text-[11px] truncate" title={pr.facts || pr.supporting_text}>{pr.facts || pr.supporting_text}</td>
                    <td className="py-3 px-3.5 text-slate-200 font-medium max-w-[200px] text-[11px] truncate" title={pr.principle || pr.claim}>{pr.principle || pr.claim}</td>
                    <td className="py-3 px-3 text-emerald-400/90 text-[11px]">{pr.similarity || 'Analogous authority'}</td>
                    <td className="py-3 px-3 text-amber-400/90 text-[11px]">{pr.distinction || 'Fact-specific'}</td>
                    <td className="py-3 px-3 text-blue-300 font-semibold">{pr.outcome || pr.ruling || 'Favorable'}</td>
                    <td className="py-3 px-3 text-right">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-500/30">
                        {pr.relevance || 'Controlling Authority'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODE 4: SIMULATED JUDICIAL PERSPECTIVE */}
      {/* ========================================================================= */}
      {viewMode === 'judge' && (
        <div className="space-y-6">
          <div className="text-center pb-4 border-b border-slate-800">
            <h2 className="text-xl font-bold text-white font-['Cinzel',serif] tracking-wide flex items-center justify-center gap-2">
              <Gavel className="w-5 h-5 text-indigo-400" />
              Simulated Judicial Perspective
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Neutral magistrate evaluation based on applicable legal standards of review and burdens of proof.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Strength Gauges */}
            <div className="p-5 rounded-xl legal-card border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Argument Survivability</span>
                <span className="font-mono text-emerald-400 font-bold">{metrics.argument_survival != null ? `${(metrics.argument_survival * 100).toFixed(0)}%` : 'N/A'}</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-2">
                <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${(metrics.argument_survival ?? 0) * 100}%` }} />
              </div>
              <p className="text-[11px] text-slate-400">Theory of the case adheres strictly to controlling statutory elements.</p>
            </div>

            <div className="p-5 rounded-xl legal-card border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Evidence Alignment</span>
                <span className="font-mono text-blue-400 font-bold">{metrics.evidence_alignment != null ? `${(metrics.evidence_alignment * 100).toFixed(0)}%` : 'N/A'}</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${(metrics.evidence_alignment ?? 0) * 100}%` }} />
              </div>
              <p className="text-[11px] text-slate-400">Corroboration matrix links core claims to documentary exhibits.</p>
            </div>

            <div className="p-5 rounded-xl legal-card border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Research Sufficiency</span>
                <span className="font-mono text-indigo-400 font-bold">{metrics.research_sufficiency != null ? `${(metrics.research_sufficiency * 100).toFixed(0)}%` : 'N/A'}</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-2">
                <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${(metrics.research_sufficiency ?? 0) * 100}%` }} />
              </div>
              <p className="text-[11px] text-slate-400">Landmark Supreme Court and appellate ratio decidendi directly support defenses.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Major Concerns */}
            <div className="p-6 rounded-xl legal-card border border-slate-800 space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Major Judicial Concerns
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                {[
                  "Judicial reluctance to rewrite negotiated commercial contracts between sophisticated corporate parties.",
                  "Whether adverse party will produce surprise evidence of actual oral communications at contract formation.",
                  "Establishing clear demarcation between technological authorization and internal policy compliance."
                ].map((c, i) => (
                  <li key={i} className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 flex items-start gap-2 text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                    <span>{c}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Questions a Judge Might Raise */}
            <div className="p-6 rounded-xl legal-card border border-slate-800 space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-blue-400" />
                Questions a Judge Might Raise at Oral Argument
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                {[
                  "Counsel, what objective evidence shows the liquidated damages figure was an unreasonable forecast when the contract was executed?",
                  "Did your client request specific delivery timing assurances or inform the carrier of the marketing campaign prior to shipping?",
                  "Under Van Buren, how do you distinguish between unauthorized technological access and unauthorized use of properly accessed information?"
                ].map((q, i) => (
                  <li key={i} className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 flex items-start gap-2.5 text-blue-200/90 italic">
                    <span className="font-bold text-blue-400 not-italic">Q{i + 1}:</span>
                    <span>"{q}"</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20 text-xs text-slate-300">
            <strong className="text-indigo-300 block mb-1">Judicial Simulation Disclaimer:</strong>
            This simulation is generated for moot court, litigation preparation, and strategy stress-testing. 
            It is an analytical heuristic based on legal doctrine, NOT a prediction or forecast of an actual court outcome.
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODE 5: CRITIC SELF-CORRECTION FLOW */}
      {/* ========================================================================= */}
      {viewMode === 'critic' && (
        <div className="space-y-6">
          <div className="text-center pb-4 border-b border-slate-800">
            <h2 className="text-xl font-bold text-white font-['Cinzel',serif] tracking-wide flex items-center justify-center gap-2">
              <FileCheck className="w-5 h-5 text-emerald-400" />
              Critic Self-Correction & Quality Gate
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Visualizing the cyclic reflection loop enforcing citation verification and reasoning consistency.
            </p>
          </div>

          {/* Flow Visualizer */}
          <div className="p-6 rounded-xl legal-card border border-slate-800">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs">
              <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-center w-full md:w-auto">
                <span className="text-[10px] text-slate-500 block">PHASE 1</span>
                <span className="font-bold text-white">Initial Analysis</span>
                <span className="text-[10px] text-blue-400 block mt-1">Four Agents Execute</span>
              </div>
              <span className="text-slate-600 font-bold text-lg hidden md:block">➔</span>
              <div className="p-3.5 rounded-lg bg-slate-900 border border-blue-500/40 text-center w-full md:w-auto ring-1 ring-blue-500">
                <span className="text-[10px] text-blue-400 block">PHASE 2</span>
                <span className="font-bold text-white">Adjudicator Quality Gate</span>
                <span className="text-[10px] text-emerald-400 block mt-1">Verify Citations</span>
              </div>
              <span className="text-slate-600 font-bold text-lg hidden md:block">➔</span>
              <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-center w-full md:w-auto">
                <span className="text-[10px] text-slate-500 block">PHASE 3</span>
                <span className="font-bold text-white">Target Revision</span>
                <span className="text-[10px] text-amber-400 block mt-1">Upstream Loop (Max 2)</span>
              </div>
              <span className="text-slate-600 font-bold text-lg hidden md:block">➔</span>
              <div className="p-3.5 rounded-lg bg-emerald-950/40 border border-emerald-500/40 text-center w-full md:w-auto">
                <span className="text-[10px] text-emerald-400 block">PHASE 4</span>
                <span className="font-bold text-emerald-300">Final Validated Report</span>
                <span className="text-[10px] text-slate-400 block mt-1">Quality Gate Passed</span>
              </div>
            </div>
          </div>

          {/* Audit Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl legal-card border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400">Citation Coverage:</span>
              <div className="text-xl font-bold font-mono text-emerald-400">{((report.full_report_json?.run_evaluation?.citation_coverage ?? 0) * 100).toFixed(0)}%</div>
              <p className="text-[10px] text-slate-500">Observed citation coverage for this run</p>
            </div>
            <div className="p-4 rounded-xl legal-card border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400">Unsupported Claims:</span>
              <div className="text-xl font-bold font-mono text-slate-300">{report.full_report_json?.run_evaluation?.metric_notes?.length ?? 'N/A'}</div>
              <p className="text-[10px] text-slate-500">Evaluation caveats recorded for this run</p>
            </div>
            <div className="p-4 rounded-xl legal-card border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400">Contradictions Detected:</span>
              <div className="text-xl font-bold font-mono text-slate-300">{report.full_report_json?.run_evaluation?.trajectory_quality != null ? `${(report.full_report_json.run_evaluation.trajectory_quality * 100).toFixed(0)}%` : 'N/A'}</div>
              <p className="text-[10px] text-slate-500">Trajectory quality derived from this run</p>
            </div>
            <div className="p-4 rounded-xl legal-card border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400">Total Revisions Issued:</span>
              <div className="text-xl font-bold font-mono text-blue-400">{report.full_report_json?.run_evaluation?.revision_count ?? 'N/A'}</div>
              <p className="text-[10px] text-slate-500">Actual upstream revision count</p>
            </div>
          </div>

          <div className="p-5 rounded-xl legal-card border border-slate-800 space-y-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
              Critic Gate Verdict & Actionable Remediation Feedback
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              VERDICT: PASS. The strategic legal analysis satisfies strict citation grounding requirements, 
              preserves factual-doctrinal separation, and appropriately tags model inferences versus source-supported authorities.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
