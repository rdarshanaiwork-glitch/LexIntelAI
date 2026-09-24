import json
from typing import Any, Dict


def compact_json(value: Any, limit: int = 12000) -> str:
    """Serialize structured agent state without the old 400/500-char truncation bug."""
    try:
        text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    except Exception:
        text = str(value)
    if len(text) <= limit:
        return text
    # Keep both the beginning (facts/issues) and end (latest findings/decisions).
    head = int(limit * 0.72)
    tail = limit - head
    return text[:head] + "\n...[context compacted]...\n" + text[-tail:]


def agent_context(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "case": state.get("case_context", {}),
        "objective": state.get("user_query", ""),
        "strategy": state.get("execution_strategy", "full_litigation"),
        "intake": {
            "issues": state.get("identified_issues", []),
            "facts": state.get("evidence_facts", []),
            "gaps": state.get("evidentiary_gaps", []),
        },
        "research": {
            "findings": state.get("research_findings", {}),
            "sources": state.get("retrieved_sources", []),
            "queries": state.get("search_queries_used", []),
            "unresolved": state.get("unresolved_issues", []),
        },
        "advocacy": {
            "theory": state.get("case_theory", {}),
            "counterarguments": state.get("counterarguments", {}),
            "self_assessment": state.get("self_assessment", {}),
        },
        "revision": state.get("revision_history", []),
    }
