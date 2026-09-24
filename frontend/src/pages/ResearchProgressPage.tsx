import React, { useEffect, useState } from 'react';
import { 
  ArrowLeft, BrainCircuit, CheckCircle2, FileText, 
  ArrowRight, Layers 
} from 'lucide-react';
import { api } from '../services/api';
import { ResearchSession } from '../types';
import { AgentPipelineVisualizer } from '../components/AgentPipelineVisualizer';
import { AgentOutputFormatter } from '../components/AgentOutputFormatter';

interface ResearchProgressPageProps {
  caseId: string;
  sessionId: string;
  onNavigate: (view: string, caseId?: string, sessionId?: string, reportId?: string) => void;
}

export const ResearchProgressPage: React.FC<ResearchProgressPageProps> = ({
  caseId,
  sessionId,
  onNavigate
}) => {
  const [session, setSession] = useState<ResearchSession | null>(null);
  const [selectedAgentName, setSelectedAgentName] = useState<string>('CaseIntakeAgent');
  const [selectedAgentData, setSelectedAgentData] = useState<any>(null);

  useEffect(() => {
    loadSession();
    const interval = setInterval(loadSession, 1500);
    return () => clearInterval(interval);
  }, [sessionId]);

  const loadSession = async () => {
    try {
      const data = await api.getResearchSession(sessionId);
      setSession(data);
      if (data.agent_executions?.length > 0 && !selectedAgentData) {
        setSelectedAgentName(data.agent_executions[0].agent_name);
        setSelectedAgentData(data.agent_executions[0].output_payload_json);
      }
    } catch (err) {
      console.error('Failed to poll research session', err);
    }
  };

  const handleSelectAgent = (agentName: string, data: any) => {
    setSelectedAgentName(agentName);
    setSelectedAgentData(data);
  };

  if (!session) {
    return (
      <div className="p-16 text-center text-slate-400 text-xs animate-pulse">
        Initializing Multi-Agent LangGraph Deliberation...
      </div>
    );
  }

  const isCompleted = session.status === 'completed';
  const reportId = session.reports?.[0]?.id;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('workspace', caseId)}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white font-['Cinzel',serif]">
                Multi-Agent Deliberation & Intelligence Generation
              </h1>
              <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${
                isCompleted ? 'bg-emerald-950 text-emerald-300 border-emerald-500/40' : 'bg-blue-950 text-blue-300 border-blue-500/40 animate-pulse'
              }`}>
                {session.status}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              LangGraph State Graph • Iteration Count: {session.iteration_count}
            </p>
          </div>
        </div>

        {isCompleted && reportId && (
          <button
            onClick={() => onNavigate('report-viewer', caseId, sessionId, reportId)}
            className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/25 transition-all flex items-center gap-2 self-start sm:self-auto"
          >
            <FileText className="w-4 h-4" />
            <span>View Full Legal Intelligence Report</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Per-run evaluation metrics — calculated from this exact trajectory */}
      {session.state_snapshot?.run_evaluation && (
        <div className="legal-card p-5 rounded-xl border border-cyan-900/60 bg-cyan-950/10">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">Live Evaluation — This Run</h3>
              <p className="text-[10px] text-slate-400">Computed from observed agent trajectory, evidence provenance, citations, routing and actual LLM/tool activity. No fixed scores.</p>
            </div>
            <span className="text-[10px] font-mono text-cyan-300">DYNAMIC / RUN-SPECIFIC</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
            {[
              ['Solve', 'task_solve_rate'], ['Req(D)', 'requirements_met_dependency_aware'], ['Self-stop', 'self_termination'],
              ['Evidence', 'evidence_coverage'], ['Alignment', 'evidence_alignment'], ['Authority', 'authority_coverage'],
              ['Citations', 'citation_validity'], ['Research', 'research_sufficiency']
            ].map(([label,key]) => { const v=(session.state_snapshot?.run_evaluation as any)?.[key]; return <div key={key} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800"><div className="text-[9px] text-slate-500">{label}</div><div className="text-sm font-bold text-cyan-300 mt-1">{typeof v === 'number' ? `${(v*100).toFixed(0)}%` : 'N/A'}</div></div> })}
          </div>
          <div className="flex flex-wrap gap-4 mt-3 text-[10px] text-slate-400">
            <span>Steps: {(session.state_snapshot?.run_evaluation as any)?.total_steps ?? 0}</span>
            <span>LLM calls: {(session.state_snapshot?.run_evaluation as any)?.llm_calls ?? 0}</span>
            <span>Tool calls: {(session.state_snapshot?.run_evaluation as any)?.tool_calls ?? 0}</span>
            <span>Retries: {(session.state_snapshot?.run_evaluation as any)?.retries ?? 0}</span>
            <span>Latency: {(session.state_snapshot?.run_evaluation as any)?.latency_ms ?? 0} ms</span>
            <span>Revisions: {(session.state_snapshot?.run_evaluation as any)?.revision_count ?? 0}</span>
          </div>
        </div>
      )}

      {/* Visual Pipeline Showcase */}
      <AgentPipelineVisualizer
        executions={session.agent_executions || []}
        currentAgent={session.current_agent}
        status={session.status}
        onSelectAgent={handleSelectAgent}
      />

      {/* Live Step Progression & Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Execution Timeline */}
        <div className="legal-card p-5 rounded-xl border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" />
            <span>Department Execution Log ({session.agent_executions?.length || 0} trajectory steps)</span>
          </h3>
          <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
            {session.agent_executions?.map((exec, idx) => (
              <div
                key={exec.id || idx}
                onClick={() => handleSelectAgent(exec.agent_name, exec.output_payload_json)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                  selectedAgentName === exec.agent_name
                    ? 'bg-blue-950/60 border-blue-500/60 text-white'
                    : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold">{exec.step_number}. {exec.agent_name}</span>
                  <span className="text-[10px] text-emerald-400 font-mono">{exec.execution_time_ms}ms</span>
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  <span>Structured Output Emitted</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Selected Agent Structured Output Preview */}
        <div className="lg:col-span-2 legal-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-indigo-400" />
                <span>Agent Payload Inspector: {selectedAgentName}</span>
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Validated Pydantic structured output returned to the LangGraph state
              </p>
            </div>
          </div>

          <AgentOutputFormatter agentName={selectedAgentName} data={selectedAgentData} />
        </div>
      </div>
    </div>
  );
};