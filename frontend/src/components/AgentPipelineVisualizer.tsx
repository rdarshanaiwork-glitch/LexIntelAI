import React, { useState } from 'react';
import { 
  CheckCircle2, Clock, RefreshCw, 
  BrainCircuit, Search, BookOpen, Scale, FileSearch, Target, 
  ShieldAlert, Gavel, FileCheck, FileText, ChevronDown
} from 'lucide-react';
import { AgentExecution } from '../types';
import { AgentOutputFormatter } from './AgentOutputFormatter';

interface AgentPipelineVisualizerProps {
  executions: AgentExecution[];
  currentAgent?: string;
  status?: string;
  onSelectAgent?: (agentName: string, data: any) => void;
}

interface StepMeta {
  id: string;
  name: string;
  label: string;
  role: string;
  icon: React.ElementType;
  description: string;
}

const PIPELINE_STEPS: StepMeta[] = [
  { id: 'case', name: 'CaseContext', label: 'CASE EXHIBITS', role: 'Factual Ingestion', icon: FileSearch, description: 'Client case intake, jurisdiction & exhibit grounding' },
  { id: 'intake', name: 'CaseIntakeAgent', label: 'DEPT 1: INTAKE & DISCOVERY', role: 'Issue & Evidence Auditor', icon: BrainCircuit, description: 'Merges Coordinator & Evidence: issue decomposition, factual support matrix & strategy triage' },
  { id: 'research', name: 'LegalResearchAgent', label: 'DEPT 2: KNOWLEDGE RETRIEVAL', role: 'Autonomous Tool-Use RAG', icon: Search, description: 'Merges Research, Statutes & Precedents: multi-turn vector search, query reformulation & stopping decisions' },
  { id: 'advocate', name: 'AdvocateAgent', label: 'DEPT 3: ADVOCACY & STRATEGY', role: 'Dialectical Self-Play', icon: Target, description: 'Merges Strategy & Red-Team Opponent: builds case theory, attacks as opposing counsel & assesses materiality' },
  { id: 'adjudicator', name: 'AdjudicatorReportingAgent', label: 'DEPT 4: ADJUDICATION & REPORTING', role: 'Judicial Gate & Report', icon: Gavel, description: 'Merges Judge, Citation Audit, Root-Cause Critic & Report: mechanical citation audit & 16-section dossier' },
];

export const AgentPipelineVisualizer: React.FC<AgentPipelineVisualizerProps> = ({
  executions,
  currentAgent,
  status,
  onSelectAgent
}) => {
  const [selectedStep, setSelectedStep] = useState<string | null>(null);

  const getStepStatus = (step: StepMeta) => {
    if (step.id === 'case') return 'completed';
    const exec = executions.find(e => e.agent_name.toLowerCase() === step.name.toLowerCase());
    if (exec) return exec.status;
    if (currentAgent && currentAgent.toLowerCase() === step.name.toLowerCase()) return 'running';
    if (status === 'completed') return 'completed';
    return 'pending';
  };

  const getExecTime = (step: StepMeta) => {
    const exec = executions.find(e => e.agent_name.toLowerCase() === step.name.toLowerCase());
    return exec ? `${exec.execution_time_ms}ms` : null;
  };

  const getExecPayload = (step: StepMeta) => {
    const exec = executions.find(e => e.agent_name.toLowerCase() === step.name.toLowerCase());
    return exec?.output_payload_json || null;
  };

  return (
    <div className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-bold text-white tracking-wide">
              MULTI-AGENT DELIBERATION PIPELINE
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            LangGraph Autonomous Agent Orchestration with Iterative Self-Critique & Reflection
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Pipeline State:</span>
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider ${
            status === 'completed' ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40' :
            status === 'failed' ? 'bg-rose-950 text-rose-300 border border-rose-500/40' :
            'bg-blue-950 text-blue-300 border border-blue-500/40 animate-pulse'
          }`}>
            {status || 'Active'}
          </span>
        </div>
      </div>

      {/* Visual Pipeline Grid / Chain */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5 items-stretch">
        {PIPELINE_STEPS.map((step, idx) => {
          const stepStatus = getStepStatus(step);
          const time = getExecTime(step);
          const Icon = step.icon;
          const isSelected = selectedStep === step.id;

          let cardBorder = 'border-slate-800 hover:border-slate-700 bg-slate-900/40';
          let iconColor = 'text-slate-500';
          let textColor = 'text-slate-400';

          const isRetrying = stepStatus === 'retrying' || (currentAgent && currentAgent.toLowerCase().includes('retry') && currentAgent.toLowerCase().includes(step.name.toLowerCase()));

          if (stepStatus === 'completed') {
            cardBorder = 'border-emerald-500/40 bg-emerald-950/20 hover:border-emerald-500/60 shadow-[0_0_12px_rgba(16,185,129,0.15)]';
            iconColor = 'text-emerald-400';
            textColor = 'text-slate-200';
          } else if (isRetrying) {
            cardBorder = 'border-amber-500 bg-amber-950/40 animate-pulse shadow-[0_0_15px_rgba(245,158,11,0.3)]';
            iconColor = 'text-amber-400';
            textColor = 'text-amber-100';
          } else if (stepStatus === 'running') {
            cardBorder = 'border-blue-500 bg-blue-950/40 animate-pulse shadow-[0_0_15px_rgba(59,130,246,0.3)]';
            iconColor = 'text-blue-400';
            textColor = 'text-blue-100';
          } else if (stepStatus === 'failed') {
            cardBorder = 'border-rose-500 bg-rose-950/40 shadow-[0_0_12px_rgba(244,63,94,0.2)]';
            iconColor = 'text-rose-400';
            textColor = 'text-rose-200';
          }

          const payload = getExecPayload(step);
          let extraBadge = null;
          if (step.id === 'research' && payload) {
            const count = (payload.retrieved_sources || payload.items || []).length;
            if (count > 0) {
              extraBadge = `${count} Sources`;
            }
          } else if (step.id === 'critic' && payload) {
            if (payload.verdict === 'REVISE' || payload.status === 'REVISE') {
              extraBadge = `REVISE -> ${payload.target_agent || 'strategy'}`;
            } else if (payload.verdict === 'PASS' || payload.status === 'PASS') {
              extraBadge = 'PASS';
            }
          }

          return (
            <div
              key={step.id}
              onClick={() => {
                setSelectedStep(selectedStep === step.id ? null : step.id);
                if (onSelectAgent) onSelectAgent(step.name, payload);
              }}
              className={`cursor-pointer rounded-lg p-3 border transition-all duration-200 flex flex-col justify-between relative group ${cardBorder} ${isSelected ? 'ring-2 ring-blue-500 bg-slate-900' : ''}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className={`p-1.5 rounded-md bg-slate-950/80 ${iconColor}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex items-center">
                  {stepStatus === 'completed' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                  {isRetrying && <RefreshCw className="w-3.5 h-3.5 text-amber-400 animate-spin" />}
                  {stepStatus === 'running' && !isRetrying && <RefreshCw className="w-3.5 h-3.5 text-blue-400 animate-spin" />}
                  {stepStatus === 'pending' && <Clock className="w-3.5 h-3.5 text-slate-600" />}
                  {stepStatus === 'failed' && <Clock className="w-3.5 h-3.5 text-rose-500" />}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold tracking-wider text-blue-400/80 uppercase block">
                  Step {idx + 1}
                </span>
                <h4 className={`text-xs font-bold leading-tight mt-0.5 ${textColor}`}>
                  {step.label}
                </h4>
                <p className="text-[10px] text-slate-400 mt-1 leading-snug line-clamp-2">
                  {step.role}
                </p>
                {extraBadge && (
                  <span className="mt-1.5 inline-block text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-950 text-blue-300 border border-blue-900/60 truncate max-w-full">
                    {extraBadge}
                  </span>
                )}
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px]">
                <span className="text-slate-400 font-mono">
                  {time || (stepStatus === 'completed' ? '<1s' : '--')}
                </span>
                <ChevronDown className={`w-3 h-3 text-slate-400 transition-transform duration-200 ${isSelected ? 'rotate-180 text-blue-400' : ''}`} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Expanded Step Inspector */}
      {selectedStep && (
        <div className="mt-5 p-4 rounded-lg bg-slate-900/90 border border-blue-500/30 text-xs animate-in fade-in duration-200">
          {(() => {
            const step = PIPELINE_STEPS.find(s => s.id === selectedStep);
            if (!step) return null;
            const payload = getExecPayload(step);
            return (
              <div>
                <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <step.icon className="w-4 h-4 text-blue-400" />
                    <span className="font-bold text-white text-sm">{step.name} ({step.label})</span>
                    <span className="text-slate-400">• {step.description}</span>
                  </div>
                  <button 
                    onClick={() => setSelectedStep(null)}
                    className="text-slate-400 hover:text-white text-xs px-2 py-0.5 rounded bg-slate-800"
                  >
                    Close
                  </button>
                </div>

                {payload ? (
                  <AgentOutputFormatter agentName={step.name} data={payload} />
                ) : (
                  <div className="text-slate-400 italic p-3 text-center">
                    Agent execution data not yet captured or state snapshot empty.
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};