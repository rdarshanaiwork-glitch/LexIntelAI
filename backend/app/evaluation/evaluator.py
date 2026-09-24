import json
import logging
import os
import re
import time
from typing import Any, Dict, List

from app.tools.legal_tools import LegalToolRegistry
from app.workflows.legal_graph import legal_workflow_app

logger = logging.getLogger("lexintel.evaluation")

CURRENT_AGENTS = [
    "CaseIntakeAgent",
    "LegalResearchAgent",
    "AdvocateAgent",
    "AdjudicatorReportingAgent",
]
FULL_LITIGATION_PATH = CURRENT_AGENTS
SIMPLE_PATH = ["CaseIntakeAgent", "LegalResearchAgent", "AdjudicatorReportingAgent"]


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def _source_matches(expected: str, source: Dict[str, Any]) -> bool:
    hay = " ".join([
        source.get("title", ""), source.get("source_id", ""), source.get("content", ""),
        source.get("citation_metadata", {}).get("citation", "") if isinstance(source.get("citation_metadata"), dict) else ""
    ])
    n_exp = _norm(expected)
    n_hay = _norm(hay)
    if not n_exp:
        return False
    if n_exp in n_hay:
        return True
    tokens = [t for t in re.sub(r"[^a-z0-9]+", " ", expected.lower()).split() if len(t) > 2 or t.isdigit()]
    return bool(tokens) and all(t in hay.lower() for t in tokens)


def _safe_rate(num: float, den: float) -> float:
    return round(num / den, 3) if den else 0.0


class LexIntelEvaluator:
    """Four-agent, trajectory-based evaluator.

    The design is inspired by Agent-as-a-Judge methodology: evaluate the actual
    trajectory, requirements, routing, termination and evidence grounding rather
    than treating the final prose alone as the benchmark.
    """

    def __init__(self, dataset_path: str = None):
        dataset_path = dataset_path or os.path.join(os.path.dirname(__file__), "eval_dataset.json")
        with open(dataset_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)

    def _requirements(self, item: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        expected = FULL_LITIGATION_PATH
        history = [h.get("agent") for h in state.get("execution_history", []) if h.get("status") == "completed"]
        unique = []
        for x in history:
            if x not in unique:
                unique.append(x)
        independent = sum(1 for a in expected if a in unique) / len(expected)
        # Dependency-aware: an agent only counts if all its required predecessors
        # appeared before it at least once in the trajectory.
        dependency_ok = 0
        for idx, agent in enumerate(expected):
            try:
                pos = history.index(agent)
                deps = expected[:idx]
                if all(d in history[:pos] for d in deps):
                    dependency_ok += 1
            except ValueError:
                pass
        return {
            "expected_path": expected,
            "observed_path": unique,
            "requirements_met_independent": round(independent, 3),
            "requirements_met_dependency_aware": _safe_rate(dependency_ok, len(expected)),
        }

    def _retrieval(self, item: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        retrieved = state.get("retrieved_sources", []) or []
        expected = item.get("expected_statutes", []) + item.get("expected_precedents", [])
        matched = sum(1 for e in expected if any(_source_matches(e, r) for r in retrieved))
        retrieved_relevant = sum(1 for r in retrieved if any(_source_matches(e, r) for e in expected))
        precision = _safe_rate(retrieved_relevant, len(retrieved)) if retrieved else 0.0
        recall = _safe_rate(matched, len(expected))
        f1 = _safe_rate(2 * precision * recall, precision + recall) if precision + recall else 0.0
        return {"retrieved": len(retrieved), "expected": len(expected), "matched": matched,
                "precision": precision, "recall": recall, "f1": f1}

    def _evidence(self, state: Dict[str, Any]) -> Dict[str, Any]:
        report = state.get("final_report", {}) or {}
        citations = report.get("sources_and_citations") or report.get("citations") or []
        audits = state.get("citation_audit", []) or []
        valid = sum(1 for a in audits if a.get("is_valid"))
        grounded = sum(1 for c in citations if c.get("evidence_type") == "SUPPORTED BY SOURCE")
        coverage = _safe_rate(grounded, len(citations))
        validity = _safe_rate(valid, len(audits))
        return {"citation_count": len(citations), "audited_count": len(audits),
                "citation_validity": validity, "citation_grounding": coverage,
                "invalid_citations": len(audits) - valid}

    def _trajectory(self, item: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        hist = state.get("execution_history", []) or []
        expected = FULL_LITIGATION_PATH
        completed = [h for h in hist if h.get("status") == "completed"]
        failures = [h for h in hist if h.get("status") != "completed"]
        revisions = state.get("revision_history", []) or []
        # A self-terminating trajectory reaches Completed/failed without exceeding
        # the configured revision budget and without an infinite cycle.
        terminated = state.get("status") in {"completed", "failed"} and len(revisions) <= int(state.get("max_revisions", 2))
        solve = state.get("status") == "completed" and all(a in [h.get("agent") for h in completed] for a in expected)
        return {
            "steps": len(hist),
            "completed_steps": len(completed),
            "failed_steps": len(failures),
            "revisions": len(revisions),
            "self_termination": 1.0 if terminated else 0.0,
            "task_solve_rate": 1.0 if solve else 0.0,
            "trajectory_quality": round((sum(1 for a in expected if a in [h.get("agent") for h in completed]) / len(expected)) if expected else 0.0, 3),
        }

    def evaluate_all(self) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []
        start = time.time()
        agent_stats = {a: {"executions": 0, "successful": 0, "failed": 0, "revised": 0} for a in CURRENT_AGENTS}

        for item in self.dataset:
            t0 = time.time()
            try:
                initial_state = {
                    "session_id": f"eval-{item['id']}",
                    "case_id": item["id"],
                    "strategy_requested": item.get("execution_strategy", "full_litigation"),
                    "case_context": {
                        "case_id": item["id"], "title": item["title"],
                        "jurisdiction": item["jurisdiction"], "legal_domain": item["legal_domain"],
                        "description": item["query"],
                    },
                    "user_query": item["query"],
                    "execution_strategy": item.get("execution_strategy", "full_litigation"),
                    "uploaded_documents": [],
                    "iteration_count": 0,
                    "max_revisions": 2,
                    "execution_history": [], "revision_history": [], "errors": [],
                }
                state = legal_workflow_app.invoke(initial_state)
                status = state.get("status", "unknown")
            except Exception as exc:
                logger.exception("Evaluation scenario %s failed", item["id"])
                state = {"status": "failed", "errors": [str(exc)], "execution_history": []}
                status = "failed"

            for h in state.get("execution_history", []):
                name = h.get("agent")
                if name in agent_stats:
                    agent_stats[name]["executions"] += 1
                    if h.get("status") == "completed":
                        agent_stats[name]["successful"] += 1
                    else:
                        agent_stats[name]["failed"] += 1
            for rev in state.get("revision_history", []):
                target = {"case_intake": "CaseIntakeAgent", "legal_research": "LegalResearchAgent", "advocate": "AdvocateAgent"}.get(rev.get("target_agent"))
                if target in agent_stats:
                    agent_stats[target]["revised"] += 1

            req = self._requirements(item, state)
            ret = self._retrieval(item, state)
            ev = self._evidence(state)
            traj = self._trajectory(item, state)
            latency = int((time.time() - t0) * 1000)
            results.append({
                "id": item["id"], "title": item["title"], "scenario": item["scenario"],
                "strategy": item.get("execution_strategy", "full_litigation"), "status": status,
                "latency_ms": latency,
                "routing": req,
                "retrieval": ret,
                "evidence": ev,
                "trajectory": traj,
                "run_metrics": state.get("run_evaluation", {}),
                "verdict": state.get("verdict"),
            })

        n = max(1, len(results))
        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "architecture": {"agent_count": 4, "agents": CURRENT_AGENTS},
            "methodology": "Agent-as-a-Judge-inspired trajectory evaluation adapted to LexIntel legal workflows; not the paper's original benchmark.",
            "total_scenarios": len(results),
            "workflow_success_rate": round(sum(r["status"] == "completed" for r in results) / n, 3),
            "requirements_met_independent": round(sum(r["routing"]["requirements_met_independent"] for r in results) / n, 3),
            "requirements_met_dependency_aware": round(sum(r["routing"]["requirements_met_dependency_aware"] for r in results) / n, 3),
            "task_solve_rate": round(sum(r["trajectory"]["task_solve_rate"] for r in results) / n, 3),
            "self_termination_rate": round(sum(r["trajectory"]["self_termination"] for r in results) / n, 3),
            "trajectory_quality": round(sum(r["trajectory"]["trajectory_quality"] for r in results) / n, 3),
            "retrieval_precision": round(sum(r["retrieval"]["precision"] for r in results) / n, 3),
            "retrieval_recall": round(sum(r["retrieval"]["recall"] for r in results) / n, 3),
            "retrieval_f1": round(sum(r["retrieval"]["f1"] for r in results) / n, 3),
            "citation_validity_rate": round(sum(r["evidence"]["citation_validity"] for r in results) / n, 3),
            "citation_grounding_rate": round(sum(r["evidence"]["citation_grounding"] for r in results) / n, 3),
            "average_latency_ms": int(sum(r["latency_ms"] for r in results) / n),
            "average_llm_calls": round(sum((r.get("run_metrics") or {}).get("llm_calls", 0) for r in results) / n, 1),
            "average_tool_calls": round(sum((r.get("run_metrics") or {}).get("tool_calls", 0) for r in results) / n, 1),
            "average_revisions": round(sum((r.get("run_metrics") or {}).get("revision_count", 0) for r in results) / n, 1),
            "average_research_sufficiency": round(sum(((r.get("run_metrics") or {}).get("research_sufficiency") or 0) for r in results) / n, 3),
            "agent_reliability": agent_stats,
            "scenario_breakdown": results,
            "total_evaluation_time_seconds": round(time.time() - start, 2),
        }
        out_file = os.path.join(os.path.dirname(__file__), "eval_results.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        return summary


if __name__ == "__main__":
    print(json.dumps(LexIntelEvaluator().evaluate_all(), indent=2))
