import time
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.workflows.state import LegalWorkflowState
from app.agents.case_intake import CaseIntakeAgent
from app.agents.legal_research import LegalResearchAgent
from app.agents.advocate import AdvocateAgent
from app.agents.adjudicator_reporting import AdjudicatorReportingAgent
from app.evaluation.run_metrics import calculate_run_metrics
from app.core.providers.remote import GeminiLLMProvider, GroqLLMProvider

logger = logging.getLogger("lexintel.graph")

def _build_agents():
    # Pure Gemini Architecture:
    # All 4 agents use Gemini Flash-Lite (gemini-flash-lite-latest),
    # which has high RPM/TPM limits, lowest latency, and avoids 429/503 errors.
    gemini_provider = GeminiLLMProvider(model="gemini-flash-lite-latest")
    logger.info("Initializing All Agents with Pure Gemini Flash-Lite (gemini-flash-lite-latest)")
    return (
        CaseIntakeAgent(llm_provider=gemini_provider),
        LegalResearchAgent(llm_provider=gemini_provider),
        AdvocateAgent(llm_provider=gemini_provider),
        AdjudicatorReportingAgent(llm_provider=gemini_provider),
    )

case_intake_agent, legal_research_agent, advocate_agent, adjudicator_reporting_agent = _build_agents()

AGENT_IDS = {
    "case_intake": "CaseIntakeAgent",
    "legal_research": "LegalResearchAgent",
    "advocate": "AdvocateAgent",
    "adjudicator_reporting": "AdjudicatorReportingAgent",
}


def _history(state: LegalWorkflowState, name: str, res: Dict[str, Any], is_revision: bool = False):
    history = list(state.get("execution_history", []))
    history.append({
        "agent": name,
        "time_ms": res.get("execution_time_ms", 0),
        "status": res.get("status", "failed"),
        "is_revision": is_revision,
        "error": res.get("error"),
        "output_payload": res.get("data", {}),
        "llm_calls": res.get("llm_calls", 0),
        "retries": res.get("retries", 0),
    })
    return history


def _completed(state: LegalWorkflowState, agent_id: str):
    completed = list(state.get("completed_agents", []))
    completed.append(AGENT_IDS[agent_id])
    return completed


def node_case_intake(state: LegalWorkflowState) -> Dict[str, Any]:
    logger.info("[GRAPH] 1/4 CaseIntakeAgent")
    res = case_intake_agent.run(state)
    if res.get("status") != "completed":
        return {"status": "failed", "errors": [res.get("error", "Agent 1 failed")],
                "current_agent": "CaseIntakeAgent", "execution_history": _history(state, "CaseIntakeAgent", res)}
    data = res["data"]
    # User-selected execution strategy is authoritative.
    strategy = state.get("execution_strategy") or state.get("strategy_requested") or "full_litigation"
    return {
        "execution_strategy": strategy,
        "identified_issues": data.get("identified_issues", []),
        "legal_issues": data.get("legal_issues", []),
        "evidence_facts": data.get("evidence_facts", []),
        "evidentiary_gaps": data.get("evidentiary_gaps", []),
        "corroboration_matrix": data.get("corroboration_matrix", {}),
        "missing_information": data.get("missing_information", []),
        "intake_ready": data.get("intake_ready", True),
        "plan": data,
        "evidence_analysis": data.get("evidence_analysis", {}),
        "current_agent": "LegalResearchAgent",
        "completed_agents": _completed(state, "case_intake"),
        "execution_history": _history(state, "CaseIntakeAgent", res),
        "status": "in_progress",
        "retrying_agent": None,
    }


def node_legal_research(state: LegalWorkflowState) -> Dict[str, Any]:
    time.sleep(1.2)  # Grace period for token bucket replenishment
    is_revision = state.get("retrying_agent") == "legal_research"
    logger.info("[GRAPH] 2/4 LegalResearchAgent%s", " [REVISION]" if is_revision else "")
    res = legal_research_agent.run(state)
    if res.get("status") != "completed":
        return {"status": "failed", "errors": [res.get("error", "Agent 2 failed")],
                "current_agent": "LegalResearchAgent",
                "execution_history": _history(state, "LegalResearchAgent", res, is_revision)}
    data = res["data"]
    return {
        "research_findings": data,
        "retrieved_sources": data.get("retrieved_sources", []),
        "search_queries_used": data.get("search_queries_used", []),
        "research_coverage_assessment": data.get("coverage_assessment", ""),
        "unresolved_issues": data.get("unresolved_issues", []),
        "statute_analysis": data,
        "precedent_analysis": data,
        "research_trajectory": data.get("research_trajectory", []),
        "current_agent": "AdvocateAgent",
        "retrying_agent": None,
        "completed_agents": _completed(state, "legal_research"),
        "execution_history": _history(state, "LegalResearchAgent", res, is_revision),
        "status": "in_progress",
    }


def node_advocate(state: LegalWorkflowState) -> Dict[str, Any]:
    time.sleep(1.2)  # Grace period for token bucket replenishment
    is_revision = state.get("retrying_agent") == "advocate"
    logger.info("[GRAPH] 3/4 AdvocateAgent%s", " [REVISION]" if is_revision else "")
    res = advocate_agent.run(state)
    if res.get("status") != "completed":
        return {"status": "failed", "errors": [res.get("error", "Agent 3 failed")],
                "current_agent": "AdvocateAgent",
                "execution_history": _history(state, "AdvocateAgent", res, is_revision)}
    data = res["data"]
    return {
        "case_theory": data.get("case_theory", {}),
        "counterarguments": data.get("counterarguments", {}),
        "self_assessment": data.get("self_assessment", {}),
        "revision_log": data.get("revision_log", []),
        "strategy": data.get("strategy", data.get("case_theory", {})),
        "affirmative_arguments": data.get("affirmative_arguments", []),
        "current_agent": "AdjudicatorReportingAgent",
        "retrying_agent": None,
        "completed_agents": _completed(state, "advocate"),
        "execution_history": _history(state, "AdvocateAgent", res, is_revision),
        "status": "in_progress",
    }


def node_adjudicator_reporting(state: LegalWorkflowState) -> Dict[str, Any]:
    time.sleep(1.2)  # Grace period for token bucket replenishment
    logger.info("[GRAPH] 4/4 AdjudicatorReportingAgent")
    res = adjudicator_reporting_agent.run(state)
    if res.get("status") != "completed":
        return {"status": "failed", "errors": [res.get("error", "Agent 4 failed")],
                "current_agent": "AdjudicatorReportingAgent",
                "execution_history": _history(state, "AdjudicatorReportingAgent", res)}
    data = res["data"]
    verdict = data.get("verdict", "PASS")
    target = data.get("target_agent")
    iteration = int(state.get("iteration_count", 0))
    max_revisions = int(state.get("max_revisions", getattr(settings, "MAX_REVISIONS", 0)))
    revision_history = list(state.get("revision_history", []))

    if verdict == "REVISE" and target and iteration < max_revisions:
        iteration += 1
        revision_history.append({
            "iteration": iteration,
            "target_agent": target,
            "reason": data.get("remediation_instructions", ""),
        })
        status = "retrying"
        retrying = target
        current = {
            "case_intake": "CaseIntakeAgent",
            "legal_research": "LegalResearchAgent",
            "advocate": "AdvocateAgent",
        }.get(target, "LegalResearchAgent")
    else:
        status = "inconclusive" if verdict == "REVISE" else "completed"
        retrying = None
        current = "Inconclusive — material issues remain" if status == "inconclusive" else "Completed"

    metrics_state = dict(state)
    metrics_state.update({
        **data,
        "verdict": verdict,
        "status": status,
        "execution_history": _history(state, "AdjudicatorReportingAgent", res),
        "revision_history": revision_history,
    })
    run_metrics = calculate_run_metrics(metrics_state)

    history_res = dict(res)
    history_res["data"] = {**data, "run_evaluation": run_metrics}

    return {
        "run_evaluation": run_metrics,
        "merits_evaluation": data.get("merits_evaluation", {}),
        "citation_audit": data.get("citation_audit", []),
        "root_cause": data.get("root_cause", {}),
        "verdict": verdict,
        "remediation_instructions": data.get("remediation_instructions", ""),
        "passed_quality_gate": verdict == "PASS" and status == "completed",
        "revision_required": verdict == "REVISE",
        "invalid_citation_count": data.get("invalid_citation_count", 0),
        "final_report": {**(data.get("final_report", {}) or {}), "run_evaluation": run_metrics},
        "citations": data.get("citations", []),
        "judge_evaluation": data.get("judge_evaluation", {}),
        "critic_feedback": data.get("critic_feedback", {}),
        "target_agent": target,
        "retrying_agent": retrying,
        "revision_history": revision_history,
        "iteration_count": iteration,
        "current_agent": current,
        "status": status,
        "execution_history": _history(state, "AdjudicatorReportingAgent", history_res),
    }


def route_after_research(state: LegalWorkflowState) -> Literal["advocate", "adjudicator_reporting"]:
    strategy = state.get("execution_strategy") or state.get("strategy_requested")
    if strategy == "simple_inquiry":
        return "adjudicator_reporting"
    return "advocate"


def route_after_adjudicator(state: LegalWorkflowState) -> Literal["case_intake", "legal_research", "advocate", "end"]:
    if state.get("status") in {"failed", "inconclusive"}:
        return "end"
    verdict = state.get("verdict", "PASS")
    target = state.get("retrying_agent")
    iteration = int(state.get("iteration_count", 0))
    max_revisions = int(state.get("max_revisions", getattr(settings, "MAX_REVISIONS", 0)))
    if verdict == "REVISE" and target and iteration < max_revisions:
        return target if target in {"case_intake", "legal_research", "advocate"} else "legal_research"
    return "end"


def build_legal_graph():
    builder = StateGraph(LegalWorkflowState)
    builder.add_node("case_intake", node_case_intake)
    builder.add_node("legal_research", node_legal_research)
    builder.add_node("advocate", node_advocate)
    builder.add_node("adjudicator_reporting", node_adjudicator_reporting)
    builder.set_entry_point("case_intake")
    builder.add_edge("case_intake", "legal_research")
    builder.add_conditional_edges("legal_research", route_after_research, {
        "advocate": "advocate",
        "adjudicator_reporting": "adjudicator_reporting",
    })
    builder.add_edge("advocate", "adjudicator_reporting")
    builder.add_conditional_edges("adjudicator_reporting", route_after_adjudicator, {
        "case_intake": "case_intake",
        "legal_research": "legal_research",
        "advocate": "advocate",
        "end": END,
    })
    return builder.compile()


legal_workflow_app = build_legal_graph()
