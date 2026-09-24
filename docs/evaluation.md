# LexIntel Evaluation

The current evaluator is a **four-agent trajectory benchmark**. It is inspired by the trajectory-oriented methodology of Agent-as-a-Judge, but it is an adaptation for LexIntel's legal domain.

## Current path

Full litigation:
`CaseIntakeAgent → LegalResearchAgent → AdvocateAgent → AdjudicatorReportingAgent`

Simple inquiry:
`CaseIntakeAgent → LegalResearchAgent → AdjudicatorReportingAgent`

## Metrics

1. Requirements Met — Independent
2. Requirements Met — Dependency-aware
3. Task Solve Rate
4. Self-Termination
5. Trajectory Quality
6. Retrieval Precision
7. Retrieval Recall
8. Retrieval F1
9. Citation Validity
10. Citation Grounding
11. Agent Reliability
12. Latency

## Important interpretation rule

Do not hard-code or claim 100% performance before a fresh benchmark run. The repository starts with an explicit `not_run` result so the Evaluation dashboard cannot accidentally display stale historical numbers.

Run a fresh benchmark with:

```bash
cd backend
python -m app.evaluation.evaluator
```
