from app.workflows.legal_graph import legal_workflow_app, route_after_research, route_after_adjudicator


def make_state(strategy="full_litigation"):
    return {
        "session_id": "test-session",
        "case_id": "test-case",
        "strategy_requested": strategy,
        "case_context": {
            "case_id": "test-case",
            "title": "Vance v. Sterling BioPharm",
            "jurisdiction": "US Federal",
            "legal_domain": "Whistleblower Retaliation",
            "description": "Contractor reports regulatory misconduct and is terminated.",
        },
        "user_query": "Does SOX section 1514A protect contractor employees under Lawson v. FMR LLC?",
        "execution_strategy": strategy,
        "uploaded_documents": [],
        "iteration_count": 0,
        "max_revisions": 2,
        "execution_history": [],
        "revision_history": [],
        "errors": [],
    }


def test_full_litigation_route_is_exactly_1_2_3_4():
    assert route_after_research(make_state("full_litigation")) == "advocate"
    final_state = legal_workflow_app.invoke(make_state("full_litigation"))
    assert final_state["status"] == "completed"
    names = [h["agent"] for h in final_state["execution_history"]]
    assert names[0:4] == [
        "CaseIntakeAgent", "LegalResearchAgent", "AdvocateAgent", "AdjudicatorReportingAgent"
    ]
    assert "AdvocateAgent" in names
    assert final_state.get("case_theory")
    assert final_state.get("counterarguments")
    assert final_state.get("self_assessment")
    assert final_state.get("final_report")


def test_simple_inquiry_intentionally_skips_advocate():
    assert route_after_research(make_state("simple_inquiry")) == "adjudicator_reporting"
    final_state = legal_workflow_app.invoke(make_state("simple_inquiry"))
    assert final_state["status"] == "completed"
    names = [h["agent"] for h in final_state["execution_history"]]
    assert names[0:3] == ["CaseIntakeAgent", "LegalResearchAgent", "AdjudicatorReportingAgent"]
    assert "AdvocateAgent" not in names


def test_revision_routing_is_targeted_and_bounded():
    state = make_state("full_litigation")
    state.update({"status": "retrying", "verdict": "REVISE", "retrying_agent": "advocate", "iteration_count": 1, "max_revisions": 2})
    assert route_after_adjudicator(state) == "advocate"
    state.update({"iteration_count": 2})
    assert route_after_adjudicator(state) == "advocate"
    state.update({"iteration_count": 3})
    assert route_after_adjudicator(state) == "end"
