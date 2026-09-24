import React, { useState } from 'react';
import { 
  Scale, Shield, BrainCircuit, Users, FileCheck, Gavel, 
  ArrowRight, Sparkles, Database, Layers, CheckCircle2, 
  BookOpen, Search, AlertCircle, Award, BarChart3
} from 'lucide-react';

interface LandingPageProps {
  onEnter: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onEnter }) => {
  const [activeAgent, setActiveAgent] = useState<number>(0);

  const agentsList = [
    {
      name: "CaseIntakeAgent",
      dept: "Department 1",
      role: "Intake & Discovery Department",
      covers: "Merges Coordinator & Evidence Auditor",
      icon: BrainCircuit,
      color: "text-blue-400",
      bg: "bg-blue-950/60 border-blue-800/50",
      description: "Jointly decomposes legal issues directly from exhibit metrics and client narratives. Rates issue-by-issue evidentiary support (strong/moderate/weak/none) and operates inside the mandatory Full Litigation pipeline and determines what facts, issues, and evidence are actually established."
    },
    {
      name: "LegalResearchAgent",
      dept: "Department 2",
      role: "Legal Knowledge & Retrieval Department",
      covers: "Merges Research Librarian, Statute & Precedent Analysts",
      icon: Search,
      color: "text-sky-400",
      bg: "bg-sky-950/60 border-sky-800/50",
      description: "Runs an autonomous multi-turn ReAct tool loop over ChromaDB vector embeddings. Evaluates prior result quality, reformulates queries into legal terminology, picks tools (statute/precedent/general), and stops autonomously when coverage is sufficient."
    },
    {
      name: "AdvocateAgent",
      dept: "Department 3",
      role: "Litigation Strategy & Advocacy Department",
      covers: "Merges Lead Trial Counsel & Red-Team Opponent",
      icon: Users,
      color: "text-rose-400",
      bg: "bg-rose-950/60 border-rose-800/50",
      description: "Performs Dialectical Self-Play: constructs a citable case theory, then swaps personas to attack its own theory as Opposing Counsel. Evaluates damage materiality (fatal vs survivable) and automatically rebuilds the theory if a fatal weakness was exposed."
    },
    {
      name: "AdjudicatorReportingAgent",
      dept: "Department 4",
      role: "Adjudication & Reporting Department",
      covers: "Merges Neutral Judge, Citation Auditor, Root-Cause Critic & Dossier Architect",
      icon: Gavel,
      color: "text-emerald-400",
      bg: "bg-emerald-950/60 border-emerald-800/50",
      description: "Evaluates merits objectively, mechanically audits citations against vector DB, attributes root-cause flaws to upstream agents, enforces PASS/REVISE quality gate loops, and compiles depth-calibrated 16-section strategic reports with grounding tags."
    }
  ];

  return (
    <div className="min-h-screen bg-[#060913] text-slate-100 flex flex-col justify-between">
      {/* Hero Section */}
      <div className="relative overflow-hidden pt-16 pb-14 px-6">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-gradient-to-tr from-blue-600/20 via-indigo-500/15 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-950/80 border border-blue-500/30 text-xs font-semibold text-blue-300 mb-6 shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span>Beyond Legal Research. Toward Legal Intelligence.</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight font-['Cinzel',serif]">
            LEXINTEL AI <br />
            <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-sky-300 bg-clip-text text-transparent">
              4-Department Multi-Agent Intelligence
            </span>
          </h1>

          <p className="mt-5 text-base sm:text-lg text-slate-300 max-w-3xl mx-auto leading-relaxed">
            An autonomous multi-agent virtual legal war room. 4 Department Super-Agents unify 10 legal reasoning roles across 
            task decomposition, statutory analysis, precedent comparison, dialectical self-play red-teaming, and judicial adjudication.
          </p>

          {/* Primary & Secondary CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={onEnter}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-blue-500/30 transition-all flex items-center justify-center gap-2 group"
            >
              <span>START CASE ANALYSIS</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={onEnter}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold text-sm transition-all flex items-center justify-center gap-2"
            >
              <BarChart3 className="w-4 h-4 text-blue-400" />
              <span>VIEW BENCHMARKS & EVALUATION</span>
            </button>
          </div>

          {/* Academic Badge */}
          <div className="mt-8 text-xs text-slate-400 flex items-center justify-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>University Capstone Project • LangGraph 4-Department State Machine • Verified Citation Grounding</span>
          </div>
        </div>
      </div>

      {/* Problem, Solution, Differentiator Section */}
      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-xl legal-card border border-rose-500/20 bg-rose-950/10 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              THE PROBLEM
            </div>
            <h3 className="text-base font-bold text-white">Fragmented & Manual Legal Research</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Traditional legal research is fragmented across siloed databases, requiring hours of manual synthesis. 
              Generic LLMs fail by hallucinating citations and lacking multi-perspective adversarial rigor.
            </p>
          </div>

          <div className="p-6 rounded-xl legal-card border border-blue-500/20 bg-blue-950/10 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              THE SOLUTION
            </div>
            <h3 className="text-base font-bold text-white">Coordinated Departmental Deliberation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              LexIntel AI coordinates 4 High-Autonomy Department Super-Agents that plan, retrieve verified authorities, 
              cross-examine evidence via dialectical self-play, and produce structured strategic intelligence dossiers.
            </p>
          </div>

          <div className="p-6 rounded-xl legal-card border border-indigo-500/20 bg-indigo-950/10 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              CORE DIFFERENTIATOR
            </div>
            <h3 className="text-base font-bold text-white">Adversarial Self-Play + Root-Cause Gate</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Real multi-agent collaboration with an Advocate Agent simulating opposing counsel and an Adjudicator Agent 
              performing mechanical citation audits and causal root-cause reflection loops before report release.
            </p>
          </div>
        </div>
      </div>

      {/* Interactive 4-Department Visual Pipeline System */}
      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-blue-400 font-semibold mb-2">
            <Layers className="w-3.5 h-3.5" />
            <span>Interactive Multi-Agent System</span>
          </div>
          <h2 className="text-2xl font-bold text-white font-['Cinzel',serif]">
            The 4 Department Super-Agents (Unifying 10 Roles)
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-xl mx-auto">
            Click on any department below to inspect its dedicated domain role and operational responsibilities.
          </p>
        </div>

        {/* Agent Selectors Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 mb-6">
          {agentsList.map((ag, idx) => {
            const Icon = ag.icon;
            const isSelected = activeAgent === idx;
            return (
              <button
                key={idx}
                onClick={() => setActiveAgent(idx)}
                className={`p-4 rounded-xl border text-left transition-all flex flex-col justify-between ${
                  isSelected 
                    ? `${ag.bg} shadow-lg shadow-blue-500/10 ring-1 ring-blue-400`
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon className={`w-4 h-4 ${ag.color}`} />
                    <span className="font-bold text-xs text-white">{ag.dept}</span>
                  </div>
                  <span className="font-mono text-[9px] text-slate-500">#{idx + 1}</span>
                </div>
                <div>
                  <div className="font-bold text-xs text-white truncate">{ag.name}</div>
                  <div className="text-[10px] text-blue-300 font-medium truncate mt-0.5">{ag.role}</div>
                  <div className="text-[9px] text-slate-400 truncate mt-1">{ag.covers}</div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Active Agent Detail Card */}
        <div className="p-6 rounded-2xl legal-card border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900/60 to-slate-950">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center">
                {React.createElement(agentsList[activeAgent].icon, { className: `w-6 h-6 ${agentsList[activeAgent].color}` })}
              </div>
              <div>
                <h3 className="text-lg font-bold text-white font-mono">{agentsList[activeAgent].name}</h3>
                <span className="text-xs text-blue-400 font-semibold">{agentsList[activeAgent].role}</span>
              </div>
            </div>
            <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-500/30">
              LangGraph State Node #{activeAgent + 1}
            </span>
          </div>

          <p className="mt-4 text-sm text-slate-300 leading-relaxed">
            {agentsList[activeAgent].description}
          </p>
        </div>
      </div>

      {/* Footer & Disclaimer */}
      <footer className="border-t border-slate-900 bg-[#04070e] py-6 px-6 text-center text-xs text-slate-400 space-y-2">
        <p className="font-semibold text-slate-300">
          LexIntel AI — Autonomous Agentic Legal Intelligence System for Strategic Legal Decision-Making.
        </p>
        <p className="text-[11px] text-slate-400 max-w-4xl mx-auto leading-relaxed">
          ACADEMIC DECISION-SUPPORT NOTICE: This system provides AI-assisted legal research and decision support for informational and academic purposes. 
          It does not constitute legal advice, does not replace a qualified legal professional, and simulated judicial assessments are not predictions of actual court decisions.
        </p>
      </footer>
    </div>
  );
};
