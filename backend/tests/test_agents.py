from app.agents import CaseIntakeAgent, LegalResearchAgent, AdvocateAgent, AdjudicatorReportingAgent


def base_state():
    return {
        "case_context": {"title": "Apex v. Horizon", "description": "Commercial contract dispute over delayed deliveries.", "jurisdiction": "Common Law", "legal_domain": "Contracts"},
        "user_query": "Analyze liquidated damages and lost goodwill exposure.",
        "execution_strategy": "full_litigation",
        "uploaded_documents": [], "iteration_count": 0, "max_revisions": 2,
        "execution_history": [], "revision_history": [], "errors": [],
    }


def test_current_agents_have_structured_outputs():
    s = base_state()
    a1 = CaseIntakeAgent().run(s); assert a1["status"] == "completed"; s.update(a1["data"])
    s["identified_issues"] = a1["data"].get("identified_issues", [])
    a2 = LegalResearchAgent().run(s); assert a2["status"] == "completed"; s.update(a2["data"])
    a3 = AdvocateAgent().run(s); assert a3["status"] == "completed"; s.update(a3["data"])
    a4 = AdjudicatorReportingAgent().run(s); assert a4["status"] == "completed"; s.update(a4["data"])
    assert a1["data"]["identified_issues"]
    assert a2["data"]["retrieved_sources"] is not None
    assert a3["data"]["case_theory"]
    assert a3["data"]["counterarguments"]
    assert a3["data"]["self_assessment"]
    assert "verdict" in a4["data"]
