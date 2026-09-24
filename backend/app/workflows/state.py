from typing import TypedDict, List, Dict, Any, Optional


class LegalWorkflowState(TypedDict, total=False):
    # Canonical request identity
    session_id: str
    case_id: str
    strategy_requested: str

    # Case context
    case_context: Dict[str, Any]
    user_query: str
    uploaded_documents: List[Dict[str, Any]]
    prior_session_memory: Optional[Dict[str, Any]]

    # Explicit orchestration state
    execution_strategy: str  # full_litigation only
    current_agent: str
    completed_agents: List[str]
    status: str
    iteration_count: int
    max_revisions: int
    retrying_agent: Optional[str]
    target_agent: Optional[str]
    revision_history: List[Dict[str, Any]]
    execution_history: List[Dict[str, Any]]
    errors: List[str]

    # Agent 1
    identified_issues: List[Dict[str, Any]]
    legal_issues: List[str]
    evidence_facts: List[Dict[str, Any]]
    evidentiary_gaps: List[str]
    corroboration_matrix: Dict[str, Any]
    missing_information: List[str]
    intake_ready: bool
    plan: Dict[str, Any]
    evidence_analysis: Dict[str, Any]

    # Agent 2
    research_findings: Dict[str, Any]
    retrieved_sources: List[Dict[str, Any]]
    search_queries_used: List[str]
    research_coverage_assessment: str
    unresolved_issues: List[str]
    statute_analysis: Dict[str, Any]
    precedent_analysis: Dict[str, Any]
    research_trajectory: List[Dict[str, Any]]

    # Agent 3
    case_theory: Dict[str, Any]
    counterarguments: Dict[str, Any]
    self_assessment: Dict[str, Any]
    revision_log: List[Dict[str, Any]]
    strategy: Dict[str, Any]
    affirmative_arguments: List[Dict[str, Any]]

    # Agent 4
    merits_evaluation: Dict[str, Any]
    citation_audit: List[Dict[str, Any]]
    root_cause: Dict[str, Any]
    verdict: str
    remediation_instructions: str
    passed_quality_gate: bool
    revision_required: bool
    judge_evaluation: Dict[str, Any]
    critic_feedback: Dict[str, Any]
    invalid_citation_count: int
    run_evaluation: Dict[str, Any]

    # Final reporting
    citations: List[Dict[str, Any]]
    final_report: Dict[str, Any]
