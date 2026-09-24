# LexIntel AI: Agent Workflow & Orchestration

LexIntel AI operates as a collaborative virtual legal team. Rather than using an unstructured prompt chain, the system decomposes strategic legal analysis into specialized autonomous personas governed by **LangGraph**.

---

## 1. The 10 Specialized Agents

### 1. CoordinatorAgent (`CoordinatorOutput`)
* **Role**: Chief Legal Strategist & Senior Partner.
* **Responsibilities**: Analyzes the dispute, selects the execution strategy (`full_litigation` vs `simple_inquiry`), breaks the problem into subtasks, assigns roles, and identifies core legal issues.
* **State Updates**: `execution_strategy`, `execution_plan`, `identified_legal_issues`.

### 2. EvidenceAgent (`EvidenceOutput`)
* **Role**: Trial Fact Auditor.
* **Responsibilities**: Examines case documents and factual statements, maps evidence to potential claims, evaluates probative weight, and flags hearsay risks or chain-of-custody defects.
* **State Updates**: `evidence_analysis`.

### 3. ResearchAgent (`ResearchOutput`)
* **Role**: Senior Law Librarian.
* **Responsibilities**: Executes search queries via `LegalToolRegistry.search_legal_knowledge()`, retrieves relevant statutory sections and case law passages, and filters by jurisdiction.
* **State Updates**: `retrieved_docs`.

### 4. StatuteAgent (`StatuteOutput`)
* **Role**: Legislative Code Analyst.
* **Responsibilities**: Dissects statutory text into prima facie elements, affirmative exceptions, and jurisdictional prerequisites.
* **State Updates**: `statutory_analysis`.

### 5. PrecedentAgent (`PrecedentOutput`)
* **Role**: Case Law Specialist.
* **Responsibilities**: Analyzes judicial opinions, extracts holdings and ratio decidendi, and draws factual analogies and distinctions with the matter at hand.
* **State Updates**: `precedent_analysis`.

### 6. StrategyAgent (`StrategyOutput`)
* **Role**: Lead Trial Counsel.
* **Responsibilities**: Synthesizes the affirmative theory of the case, outlines statutory causes of action, and proposes evidentiary and procedural steps.
* **State Updates**: `strategy_output`.

### 7. OpponentAgent (`OpponentOutput`)
* **Role**: Adversarial Red Team.
* **Responsibilities**: Simulates opposing counsel, challenges factual vulnerabilities, formulates affirmative defenses, and anticipates motions to dismiss or for summary judgment.
* **State Updates**: `opponent_analysis`.

### 8. JudgeAgent (`JudgeOutput`)
* **Role**: Neutral Magistrate / Judicial Arbiter.
* **Responsibilities**: Evaluates each claim under applicable legal standards of review and burdens of proof, producing simulated probability assessments.
* **State Updates**: `judge_evaluation`.

### 9. CriticAgent (`CriticOutput`)
* **Role**: Quality Assurance Gatekeeper.
* **Responsibilities**: Audits citation authenticity using `LegalToolRegistry.validate_citation()`, checks for logical contradictions, and issues `PASS` or `REVISE` with an assigned `target_agent`.
* **State Updates**: `critic_feedback`, `revision_history`.

### 10. ReportAgent (`ReportOutput`)
* **Role**: Dossier Architect.
* **Responsibilities**: Synthesizes all agent outputs into a standardized 16-section legal intelligence dossier with classified citations and decision-support notices.
* **State Updates**: `final_report`.

---

## 2. Dynamic LangGraph Routing Logic

### Coordinator Routing
```python
def coordinator_router(state: LegalWorkflowState) -> Literal["evidence", "research"]:
    strategy = state.get("execution_strategy", "full_litigation")
    if strategy == "simple_inquiry":
        return "research"
    return "evidence"
```

### Critic Dynamic Revision Router
```python
def critic_review_router(state: LegalWorkflowState) -> Literal["strategy", "opponent", "statute", "precedent", "research", "report"]:
    critic = state.get("critic_feedback", {})
    passed = critic.get("passed_quality_gate", True)
    revisions = state.get("revision_history", [])

    if not passed and len(revisions) < MAX_CRITIC_REVISIONS:
        target = critic.get("target_agent", "strategy")
        if target in ["strategy", "opponent", "statute", "precedent", "research"]:
            return target
        return "strategy"

    return "report"
```

This ensures that revisions are targeted directly at the agent responsible for the identified defect, while hard limits prevent unbounded cycles.
