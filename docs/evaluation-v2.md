# LexIntel Evaluation v2

The evaluation harness is inspired by the trajectory-oriented ideas in **Agent-as-a-Judge: Evaluate Agents with Agents** (arXiv:2410.10934), but the metrics are adapted to LexIntel's legal workflow and should not be presented as reproducing the paper's original benchmark.

## Metrics

- **Requirements Met (Independent):** fraction of required agents that executed successfully at least once.
- **Requirements Met (Dependency-aware):** an agent counts only when its required predecessors occurred before it.
- **Task Solve Rate:** expected workflow path completed successfully.
- **Self-Termination:** workflow reaches a terminal state without exceeding the revision budget.
- **Trajectory Quality:** expected agent path coverage.
- **Retrieval Precision / Recall / F1:** expected authorities matched against retrieved sources.
- **Citation Validity:** audited citations that resolve to the verified knowledge base.
- **Citation Grounding:** final citations explicitly marked as source-supported.
- **Agent Reliability:** executions, successes, failures and targeted revisions per current agent.
- **Latency:** end-to-end scenario runtime.

The evaluator stores the full scenario breakdown in `backend/app/evaluation/eval_results.json` and the frontend reads these fields directly.
