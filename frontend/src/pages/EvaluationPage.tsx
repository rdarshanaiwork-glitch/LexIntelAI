import React, { useState, useEffect } from 'react';
import { 
  BarChart3, CheckCircle2, ShieldCheck, Clock, RefreshCw, 
  AlertTriangle, ArrowRight, Layers, FileCheck, Award
} from 'lucide-react';
import { api } from '../services/api';

interface EvaluationPageProps {
  onNavigate: (view: string, caseId?: string) => void;
}

export const EvaluationPage: React.FC<EvaluationPageProps> = ({ onNavigate }) => {
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [running, setRunning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getEvaluationResults();
      setResults(data);
    } catch (err: any) {
      console.error('Error fetching evaluation results:', err);
      setError(err.message || 'Failed to load evaluation metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  const handleRunEvaluation = async () => {
    try {
      setRunning(true);
      setError(null);
      const freshData = await api.runEvaluation();
      setResults(freshData);
    } catch (err: any) {
      console.error('Error re-running evaluation:', err);
      setError(err.message || 'Evaluation run failed');
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-slate-400 text-sm">Loading empirical evaluation metrics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white font-['Cinzel',serif] tracking-wide">
              Empirical Evaluation & Benchmark Suite
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
              Academic Benchmark
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Quantitative validation from observed trajectories, evidence provenance, authority matching, citation audits, routing, latency and actual LLM/tool activity. No fixed per-case scores.
          </p>
        </div>

        <button
          onClick={handleRunEvaluation}
          disabled={running}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold shadow-md shadow-blue-500/25 transition-all self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${running ? 'animate-spin' : ''}`} />
          <span>{running ? 'Executing Benchmark...' : 'Re-Run Evaluation Harness'}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          ['Workflow Success', results?.workflow_success_rate, 'Uninterrupted graph completion'],
          ['Req. Met (I)', results?.requirements_met_independent, 'Agent requirements independently met'],
          ['Req. Met (D)', results?.requirements_met_dependency_aware, 'Dependency-aware routing correctness'],
          ['Task Solve Rate', results?.task_solve_rate, 'Expected workflow path solved'],
          ['Retrieval F1', results?.retrieval_f1, 'Authority precision/recall balance'],
          ['Citation Validity', results?.citation_validity_rate, 'Verified citation rate'],
        ].map(([label, value, help]) => (
          <div key={String(label)} className="p-4 rounded-xl legal-card border border-slate-800 space-y-1">
            <div className="text-slate-400 text-xs">{label}</div>
            <div className="text-2xl font-black text-white">
              {typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : '—'}
            </div>
            <p className="text-[10px] text-slate-500">{help}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          ['Self-Termination', results?.self_termination_rate],
          ['Trajectory Quality', results?.trajectory_quality],
          ['Citation Grounding', results?.citation_grounding_rate],
          ['Avg Research Sufficiency', results?.average_research_sufficiency],
          ['Avg LLM Calls', results?.average_llm_calls ?? '—'],
          ['Avg Tool Calls', results?.average_tool_calls ?? '—'],
          ['Avg Revisions', results?.average_revisions ?? '—'],
          ['Avg Latency', results?.average_latency_ms ? `${results.average_latency_ms} ms` : '—'],
        ].map(([label, value]) => (
          <div key={String(label)} className="p-4 rounded-xl legal-card border border-slate-800">
            <div className="text-xs text-slate-400">{label}</div>
            <div className="text-xl font-black text-cyan-300 mt-1">
              {typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : value}
            </div>
          </div>
        ))}
      </div>

      {/* Scenario Comparison Table */}
      <div className="p-6 rounded-xl legal-card border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Benchmark Scenario Comparison ({results?.scenario_breakdown?.length || 0} Test Matters)
          </h2>
          <span className="text-[11px] text-slate-400">
            Last evaluated: {results?.timestamp || 'N/A'}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-2.5 px-3 font-semibold">Scenario</th>
                <th className="py-2.5 px-3 font-semibold">Mode</th>
                <th className="py-2.5 px-3 font-semibold">Retrieval P / R / F1</th>
                <th className="py-2.5 px-3 font-semibold">Citation Validity</th>
                <th className="py-2.5 px-3 font-semibold">Req. Met (D)</th>
                <th className="py-2.5 px-3 font-semibold">Latency</th>
                <th className="py-2.5 px-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {results?.scenario_breakdown?.map((sc: any) => (
                <tr key={sc.id} className="hover:bg-slate-900/50 transition-colors">
                  <td className="py-3 px-3 font-medium text-white">
                    <div>{sc.scenario}</div>
                    <span className="font-mono text-[10px] text-slate-500">{sc.id}</span>
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      sc.strategy === 'full_litigation'
                        ? 'bg-blue-950/60 text-blue-400 border border-blue-800/40'
                        : 'bg-indigo-950/60 text-indigo-400 border border-indigo-800/40'
                    }`}>
                      {sc.strategy}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-200">
                    {(sc.retrieval.precision * 100).toFixed(1)} / {(sc.retrieval.recall * 100).toFixed(1)} / {(sc.retrieval.f1 * 100).toFixed(1)}
                  </td>
                  <td className="py-3 px-3 font-mono font-bold text-emerald-400">
                    {(sc.evidence.citation_validity * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3 font-mono font-bold text-blue-300">
                    {(sc.routing.requirements_met_dependency_aware * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3 font-mono text-cyan-400">
                    {sc.latency_ms} ms
                  </td>
                  <td className="py-3 px-3">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-500/30">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      {sc.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Two Column Grid: Agent Reliability & Critic Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Reliability */}
        <div className="lg:col-span-2 p-6 rounded-xl legal-card border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Award className="w-4 h-4 text-blue-400" />
              Agent Persona Reliability Matrix
            </h2>
            <span className="text-[10px] text-slate-500">4 Current Agents</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2 px-3 font-semibold">Agent Persona</th>
                  <th className="py-2 px-3 font-semibold text-center">Invocations</th>
                  <th className="py-2 px-3 font-semibold text-center">Successful</th>
                  <th className="py-2 px-3 font-semibold text-center">Failed</th>
                  <th className="py-2 px-3 font-semibold text-center">Revised</th>
                  <th className="py-2 px-3 font-semibold text-right">Reliability Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {results?.agent_reliability && Object.entries(results.agent_reliability).map(([agent, stats]: [string, any]) => {
                  const rate = stats.executions > 0 
                    ? ((stats.successful / stats.executions) * 100).toFixed(0) 
                    : '100';
                  return (
                    <tr key={agent} className="hover:bg-slate-900/40">
                      <td className="py-2.5 px-3 font-medium text-slate-200 capitalize">
                        {agent}Agent
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-slate-300">{stats.executions}</td>
                      <td className="py-2.5 px-3 text-center font-mono text-emerald-400">{stats.successful}</td>
                      <td className="py-2.5 px-3 text-center font-mono text-rose-400">{stats.failed}</td>
                      <td className="py-2.5 px-3 text-center font-mono text-amber-400">{stats.revised}</td>
                      <td className="py-2.5 px-3 text-right font-mono font-bold text-emerald-400">{rate}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Trajectory Quality */}
        <div className="p-6 rounded-xl legal-card border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Trajectory & Termination</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-xs text-slate-400">Self-Termination:</span>
              <span className="text-sm font-bold font-mono text-emerald-400">{results ? `${(results.self_termination_rate * 100).toFixed(1)}%` : '—'}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-xs text-slate-400">Task Solve Rate:</span>
              <span className="text-sm font-bold font-mono text-blue-400">{results ? `${(results.task_solve_rate * 100).toFixed(1)}%` : '—'}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-xs text-slate-400">Trajectory Quality:</span>
              <span className="text-sm font-bold font-mono text-cyan-400">{results ? `${(results.trajectory_quality * 100).toFixed(1)}%` : '—'}</span>
            </div>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Metrics are calculated from the observed LangGraph trajectory and evidence provenance; no hard-coded 10-agent assumptions remain.
          </p>
        </div>
      </div>
    </div>
  );
};
