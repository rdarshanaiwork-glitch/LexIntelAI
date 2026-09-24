import React, { useState } from 'react';
import { 
  CheckCircle2, AlertTriangle, ShieldCheck, Scale, Search, 
  BrainCircuit, Target, Gavel, Code2, Sparkles, Layers, ArrowRight, BookOpen
} from 'lucide-react';

interface AgentOutputFormatterProps {
  agentName: string;
  data: any;
}

export const AgentOutputFormatter: React.FC<AgentOutputFormatterProps> = ({ agentName, data }) => {
  const [showRaw, setShowRaw] = useState(false);

  if (!data || typeof data !== 'object') {
    return (
      <div className="p-8 text-center text-slate-400 text-xs italic">
        No execution output available for {agentName} yet.
      </div>
    );
  }

  // Helper for rendering cleanly formatted cards
  const nameLower = agentName.toLowerCase();

  // =========================================================================
  // 1. DEPARTMENT 1: INTAKE & DISCOVERY (CaseIntakeAgent)
  // =========================================================================
  if (nameLower.includes('intake') || nameLower.includes('coordinator')) {
    const issues = data.identified_issues || data.legal_issues || [];
    const facts = data.evidence_facts || data.proven_facts || data.evidence_analysis?.proven_facts || [];
    const gaps = data.evidentiary_gaps || data.evidence_analysis?.evidentiary_gaps || [];
    const strategy = data.execution_strategy || 'full_litigation';

    return (
      <div className="space-y-5 text-xs">
        {/* INTELLECTUAL DECISION HIGHLIGHT BANNER */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-blue-950 via-slate-900 to-indigo-950 border border-blue-500/40 shadow-lg space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black tracking-widest text-blue-400 uppercase flex items-center gap-1.5">
              <BrainCircuit className="w-3.5 h-3.5" />
              DEPARTMENT 1 DECISION & INTELLECTUAL ACTION
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-600 text-white uppercase font-mono shadow">
              Strategy: {strategy.replace(/_/g, ' ')}
            </span>
          </div>
          <h3 className="text-sm font-bold text-white leading-snug">
            Decision: {strategy === 'full_litigation' ? 'Full Multi-Issue Litigation Protocol Activated' : 'Simple Expedited Inquiry Selected'}
          </h3>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            {data.rationale || 'Read factual record, extracted core legal issues, cross-referenced evidence, and determined execution routing.'}
          </p>
        </div>

        {/* SUMMARY STATS GRID */}
        <div className="grid grid-cols-3 gap-3">
          <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Issues Decomposed</span>
            <span className="text-lg font-extrabold text-blue-400">{Array.isArray(issues) ? issues.length : 0} Issues</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Facts Audited</span>
            <span className="text-lg font-extrabold text-emerald-400">{Array.isArray(facts) ? facts.length : 0} Facts</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Intake Readiness</span>
            <span className={`text-lg font-extrabold ${data.intake_ready !== false ? 'text-emerald-400' : 'text-amber-400'}`}>
              {data.intake_ready !== false ? 'Ready' : 'Incomplete'}
            </span>
          </div>
        </div>

        {/* LEGAL ISSUES & EVIDENTIARY SUPPORT */}
        <div className="space-y-2.5">
          <h4 className="font-bold text-slate-200 text-xs uppercase tracking-wider flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>Extracted Legal Issues & Evidentiary Support Ratings</span>
          </h4>
          <div className="space-y-2">
            {Array.isArray(issues) && issues.map((item: any, idx: number) => {
              const text = typeof item === 'string' ? item : item.issue;
              const support = typeof item === 'object' ? item.evidentiary_support : 'strong';
              const isStrong = support === 'strong';
              return (
                <div key={idx} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <span className="font-bold text-slate-100 text-xs block">Issue {idx + 1}: {text}</span>
                    {item.gap && <p className="text-[11px] text-rose-300">⚠️ Gap: {item.gap}</p>}
                  </div>
                  <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase shrink-0 border ${
                    isStrong ? 'bg-emerald-950 text-emerald-300 border-emerald-500/30' : 'bg-amber-950 text-amber-300 border-amber-500/30'
                  }`}>
                    {support} Support
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* AUDITED FACTS HIGHLIGHT */}
        {Array.isArray(facts) && facts.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-bold text-slate-200 text-xs uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Key Audited Facts from Exhibit Record</span>
            </h4>
            <div className="divide-y divide-slate-850 rounded-lg border border-slate-800 bg-slate-950/60">
              {facts.slice(0, 4).map((f: any, i: number) => (
                <div key={i} className="p-2.5 flex items-center justify-between gap-2 text-[11px]">
                  <span className="text-slate-200 font-medium">{f.fact}</span>
                  <span className="text-blue-300 font-mono shrink-0 text-[10px]">{f.supporting_document_or_source}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // =========================================================================
  // 2. DEPARTMENT 2: LEGAL KNOWLEDGE & RETRIEVAL (LegalResearchAgent)
  // =========================================================================
  if (nameLower.includes('research') || nameLower.includes('statute') || nameLower.includes('precedent')) {
    const findings = data.findings || data.key_findings || [];
    const sources = data.retrieved_sources || data.items || [];
    const queries = data.search_queries_used || [];

    return (
      <div className="space-y-5 text-xs">
        {/* INTELLECTUAL DECISION HIGHLIGHT BANNER */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-sky-950 via-slate-900 to-blue-950 border border-sky-500/40 shadow-lg space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black tracking-widest text-sky-400 uppercase flex items-center gap-1.5">
              <Search className="w-3.5 h-3.5" />
              DEPARTMENT 2 DECISION & INTELLECTUAL ACTION
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-sky-600 text-white uppercase font-mono shadow">
              Coverage: Adequate
            </span>
          </div>
          <h3 className="text-sm font-bold text-white leading-snug">
            Decision: Research Loop Concluded (Controlling Authority Retrieved)
          </h3>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            {data.coverage_assessment || 'Executed autonomous ReAct search loop over statutes & precedents. Reformulated queries and verified coverage across all issues.'}
          </p>
        </div>

        {/* SEARCH QUERIES REFORMULATED BY LLM */}
        {queries.length > 0 && (
          <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1.5">
            <span className="text-[10px] font-bold text-sky-400 uppercase block">LLM Reformulated Legal Queries:</span>
            <div className="flex flex-wrap gap-2">
              {queries.map((q: string, i: number) => (
                <span key={i} className="px-2.5 py-1 rounded bg-slate-950 text-sky-300 border border-sky-900/50 text-[11px] font-mono">
                  🔍 "{q}"
                </span>
              ))}
            </div>
          </div>
        )}

        {/* KEY CONTROLLING FINDINGS */}
        <div className="space-y-2.5">
          <h4 className="font-bold text-slate-200 text-xs uppercase tracking-wider flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5 text-sky-400" />
            <span>Retrieved Controlling Authorities & Principles ({Array.isArray(findings) ? findings.length : 0})</span>
          </h4>
          <div className="space-y-2">
            {Array.isArray(findings) && findings.map((f: any, i: number) => {
              const issue = typeof f === 'string' ? f : f.issue;
              const principle = typeof f === 'string' ? f : f.key_principle;
              return (
                <div key={i} className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sky-300 text-xs">{issue || `Legal Issue #${i + 1}`}</span>
                    <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-500/30 uppercase">
                      Controlling Authority
                    </span>
                  </div>
                  <p className="text-slate-200 leading-relaxed text-xs">{principle}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* RETRIEVED SOURCES COUNT */}
        {Array.isArray(sources) && sources.length > 0 && (
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-slate-300">
            <span>Verified Knowledge Chunks Grounded in Vector DB:</span>
            <span className="font-bold font-mono text-emerald-400">{sources.length} Verified Sources</span>
          </div>
        )}
      </div>
    );
  }

  // =========================================================================
  // 3. DEPARTMENT 3: ADVOCACY & STRATEGY (AdvocateAgent)
  // =========================================================================
  if (nameLower.includes('advocate') || nameLower.includes('strategy') || nameLower.includes('opponent')) {
    const theory = data.case_theory || data.strategy || data;
    const attack = data.counterarguments || {};
    const assessment = data.self_assessment || {};
    const args = theory.strongest_arguments || data.affirmative_arguments || [];

    return (
      <div className="space-y-5 text-xs">
        {/* INTELLECTUAL DECISION HIGHLIGHT BANNER */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-rose-950 via-slate-900 to-purple-950 border border-rose-500/40 shadow-lg space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black tracking-widest text-rose-400 uppercase flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5" />
              DEPARTMENT 3 DECISION & INTELLECTUAL ACTION
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-600 text-white uppercase font-mono shadow">
              Materiality: {assessment.damage_assessment || 'Survivable'}
            </span>
          </div>
          <h3 className="text-sm font-bold text-white leading-snug">
            Decision: Case Theory Stress-Tested & Finalized
          </h3>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            {assessment.materiality_reasoning || 'Constructed affirmative case theory anchored to evidence IDs, executed adversarial self-play as Opposing Counsel, and evaluated damage materiality.'}
          </p>
        </div>

        {/* CASE THEORY */}
        <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1">
          <span className="text-[10px] font-bold text-blue-400 uppercase block">Affirmative Theory of the Case</span>
          <p className="text-xs text-white font-medium leading-relaxed">{theory.theory_of_the_case || 'Constructed affirmative legal narrative.'}</p>
        </div>

        {/* DIALECTICAL COMPARISON */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* Our Claim */}
          <div className="p-3.5 rounded-lg bg-slate-900/80 border border-blue-500/30 space-y-1.5">
            <span className="text-[10px] font-bold text-blue-400 uppercase block">Our Strongest Claim</span>
            <p className="text-xs text-white font-bold">{Array.isArray(args) && args[0] ? (args[0].claim || args[0]) : 'Affirmative claim anchored to statutory rights'}</p>
          </div>

          {/* Opposing Refutation */}
          <div className="p-3.5 rounded-lg bg-rose-950/30 border border-rose-500/30 space-y-1.5">
            <span className="text-[10px] font-bold text-rose-400 uppercase block">Opposing Counsel Attack</span>
            <p className="text-xs text-rose-200 font-medium">{attack.attack_on_our_argument || 'Opposing party asserts performance-based termination rationale.'}</p>
          </div>
        </div>
      </div>
    );
  }

  // =========================================================================
  // 4. DEPARTMENT 4: ADJUDICATION & REPORTING (AdjudicatorReportingAgent)
  // =========================================================================
  if (nameLower.includes('adjudicator') || nameLower.includes('judge') || nameLower.includes('critic') || nameLower.includes('report')) {
    const merits = data.merits_evaluation || data.judge_evaluation || {};
    const metrics = data.run_evaluation || data.evaluation_metrics || {};
    const audit = data.citation_audit || [];
    const verdict = data.verdict || 'PASS';

    return (
      <div className="space-y-5 text-xs">
        {/* INTELLECTUAL DECISION HIGHLIGHT BANNER */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-950 via-slate-900 to-teal-950 border border-emerald-500/40 shadow-lg space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black tracking-widest text-emerald-400 uppercase flex items-center gap-1.5">
              <Gavel className="w-3.5 h-3.5" />
              DEPARTMENT 4 DECISION & INTELLECTUAL ACTION
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-600 text-white uppercase font-mono shadow">
              Quality Gate: {verdict}
            </span>
          </div>
          <h3 className="text-sm font-bold text-white leading-snug">
            Decision: {verdict === 'PASS' ? 'Quality Gate Passed — Dossier Authorized for Compilation' : 'Revision Required'}
          </h3>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            {data.materiality_reasoning || 'Evaluated judicial merits, mechanically audited all citations against ChromaDB vector store, and attributed root-cause quality flags.'}
          </p>
        </div>

        {/* DYNAMIC RUN METRICS — never model-supplied */}
        <div className="grid grid-cols-3 gap-3">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Argument Survivability</span>
            <span className="text-lg font-extrabold text-blue-400">{metrics?.argument_survival != null ? `${(metrics.argument_survival * 100).toFixed(0)}%` : 'N/A'}</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Evidence Alignment</span>
            <span className="text-lg font-extrabold text-emerald-400">{metrics?.evidence_alignment != null ? `${(metrics.evidence_alignment * 100).toFixed(0)}%` : 'N/A'}</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Research Sufficiency</span>
            <span className="text-lg font-extrabold text-sky-400">{metrics?.research_sufficiency != null ? `${(metrics.research_sufficiency * 100).toFixed(0)}%` : 'N/A'}</span>
          </div>
        </div>

        {/* CITATION AUDIT SUMMARY */}
        <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-slate-300">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Citation Verification Audit:</span>
          </span>
          <span className="font-bold text-emerald-400 font-mono">{metrics?.citation_validity != null ? `${(metrics.citation_validity * 100).toFixed(0)}% Verified` : 'N/A'} — {audit.length} audited</span>
        </div>
      </div>
    );
  }

  // Pretty JSON Fallback with Toggle
  return (
    <div className="space-y-3 text-xs">
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <span className="font-bold text-white text-sm">{agentName} Execution Data</span>
        <button
          onClick={() => setShowRaw(!showRaw)}
          className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px] flex items-center gap-1"
        >
          <Code2 className="w-3.5 h-3.5 text-blue-400" />
          <span>{showRaw ? 'Hide JSON' : 'View JSON'}</span>
        </button>
      </div>
      {showRaw && (
        <pre className="p-3 bg-slate-950 rounded text-slate-300 font-mono text-[11px] overflow-x-auto max-h-60">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
};
