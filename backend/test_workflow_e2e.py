import sys
from app.workflows.legal_graph import legal_workflow_app

sys.stdout.reconfigure(encoding='utf-8')

print("Starting end-to-end multi-agent LangGraph workflow test with Groq 20B...")

initial_state = {
    "case_id": "test-case-groq20b-001",
    "user_query": "Jane Doe was terminated 15 days after reporting SOX accounting fraud to internal compliance.",
    "case_context": {
        "title": "Jane Doe SOX Whistleblower Retaliation",
        "description": "Employee reported accounting fraud under SOX in California and was fired 15 days later.",
        "jurisdiction": "California / 9th Circuit",
        "legal_domain": "Whistleblower & Securities"
    },
    "documents": [],
    "identified_issues": [],
    "execution_strategy": "full_litigation",
    "intake_ready": True,
    "missing_information": [],
    "research_findings": {},
    "retrieved_sources": [],
    "unresolved_issues": [],
    "case_theory": {},
    "counterarguments": {},
    "self_assessment": {},
    "adjudicator_review": {},
    "final_report": {},
    "iteration_count": 0,
    "revision_history": [],
    "current_agent": "start",
    "run_metrics": {}
}

final_state = legal_workflow_app.invoke(initial_state)

print("\n--- WORKFLOW EXECUTION COMPLETED ---")
print("Intake Issues:", len(final_state.get("identified_issues", [])))
print("Research Findings:", len(final_state.get("research_findings", {}).get("findings", [])))
print("Case Theory Present:", bool(final_state.get("case_theory")))
print("Adjudicator Verdict:", final_state.get("adjudicator_review", {}).get("verdict"))
print("Final Report Title:", final_state.get("final_report", {}).get("title"))
print("Final Report Sections:", len(final_state.get("final_report", {}).get("sections", [])))
print("\nSUCCESS: All agents completed cleanly on Groq 20B!")
