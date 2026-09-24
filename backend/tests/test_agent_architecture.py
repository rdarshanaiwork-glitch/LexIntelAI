from app.evaluation.evaluator import CURRENT_AGENTS, FULL_LITIGATION_PATH, SIMPLE_PATH


def test_current_architecture_is_four_agents():
    assert CURRENT_AGENTS == [
        "CaseIntakeAgent", "LegalResearchAgent", "AdvocateAgent", "AdjudicatorReportingAgent"
    ]
    assert FULL_LITIGATION_PATH == CURRENT_AGENTS
    assert SIMPLE_PATH == ["CaseIntakeAgent", "LegalResearchAgent", "AdjudicatorReportingAgent"]
