import os
os.environ.setdefault("LLM_PROVIDER", "mock")

from app.workflows.legal_graph import legal_workflow_app


def test_live_graph_smoke():
    state = {
        "session_id": "smoke",
        "case_id": "smoke",
        "strategy_requested": "full_litigation",
        "case_context": {"case_id": "smoke", "title": "Smoke Case", "jurisdiction": "Common Law", "legal_domain": "Contracts"},
        "user_query": "Evaluate whether a liquidated damages clause is enforceable.",
        "execution_strategy": "full_litigation",
        "uploaded_documents": [], "iteration_count": 0, "max_revisions": 2,
        "execution_history": [], "revision_history": [], "errors": [],
    }
    result = legal_workflow_app.invoke(state)
    assert result["status"] == "completed"
    assert result["final_report"]
