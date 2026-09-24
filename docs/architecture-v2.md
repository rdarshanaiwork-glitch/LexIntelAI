# LexIntel AI — Orchestration v2

## Canonical flow

### Full litigation
`CaseIntakeAgent → LegalResearchAgent → AdvocateAgent → AdjudicatorReportingAgent`

### Simple inquiry
`CaseIntakeAgent → LegalResearchAgent → AdjudicatorReportingAgent`

The selected execution strategy is authoritative at the graph level. Agent 1 may recommend a strategy for reporting, but it cannot silently change the graph topology.

## Agent responsibilities

1. **CaseIntakeAgent**
   - Decomposes facts into legal issues.
   - Audits evidence and identifies gaps.
   - Produces structured issue/evidence objects.

2. **LegalResearchAgent**
   - Runs an autonomous bounded research loop.
   - Chooses statute, precedent, general repository, or live web search based on previous results.
   - Reformulates queries and decides when coverage is sufficient.
   - Preserves the full research trajectory and provenance.

3. **AdvocateAgent**
   - Builds a case theory from the complete research package.
   - Red-teams the theory as opposing counsel.
   - Performs a materiality assessment and may rebuild the theory.
   - Produces explicit supporting arguments, counterarguments, risks and missing evidence.

4. **AdjudicatorReportingAgent**
   - Audits citations.
   - Evaluates merits, evidence and precedent strength.
   - Attributes root cause of deficiencies to an upstream agent.
   - Emits PASS/REVISE with targeted remediation.
   - On PASS, compiles a case-specific report from the complete trajectory.

## Revision routing

Agent 4 can target:
- `case_intake`
- `legal_research`
- `advocate`

Only the affected stage is re-run where possible. A hard maximum of two revisions prevents runaway loops and supports the Self-Termination metric.

## State invariant

One research request creates one canonical LangGraph state containing the case context, structured outputs, trajectory, revision history and final report. Repeated executions are stored with their own output payload instead of being reconstructed from the final state.

## Reliability rules

- Remote LLM failures are not silently converted into fake mock answers by default.
- Gemini API keys are sent through a request header rather than a URL.
- User-selected strategy cannot be overwritten by model output.
- Agent 3 is mandatory in full-litigation mode.
- Evidence/citation metrics are calculated from observed provenance.
- The evaluator contains no 10-agent assumptions.
