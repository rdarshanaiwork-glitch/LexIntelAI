# LexIntel AI — Agentic Legal Intelligence

LexIntel AI is a FastAPI + LangGraph legal decision-support system built around a **four-agent deliberative workflow**. The runtime is designed to be case-specific, tool-grounded, revisable, observable, and evaluable.

> **Decision-support notice:** this is an academic legal-AI system. It does not provide legal advice or predict actual judicial outcomes. Human legal review is required.

## 1. Canonical Agent Architecture

### Full Litigation

```text
User / Case
    │
    ▼
┌──────────────────────┐
│ 1. CaseIntakeAgent   │
│ Facts • Issues • Gaps│
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 2. LegalResearchAgent│
│ Autonomous Retrieval │
│ Statute / Precedent  │
│ / General / Live Web │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 3. AdvocateAgent     │
│ Theory → Red Team →  │
│ Materiality → Revise │
└──────────┬───────────┘
           ▼
┌──────────────────────────┐
│ 4. AdjudicatorReporting │
│ Merits + Citation Audit  │
│ Root Cause + Quality Gate│
└──────────┬───────────────┘
           │
       PASS │ REVISE
           │    └──────────────► targeted upstream agent
           ▼
       Final Report
```

### Simple Inquiry

`CaseIntakeAgent → LegalResearchAgent → AdjudicatorReportingAgent`

This is intentional. The **user-selected execution strategy is authoritative at the LangGraph routing layer**. Agent 1 can recommend complexity, but it cannot silently change a requested full-litigation graph into a simple inquiry.

## 2. What Each Agent Actually Decides

### Agent 1 — Case Intake
- Decomposes the narrative into legal issues.
- Cross-references each issue against the factual/evidentiary record.
- Identifies missing information and evidentiary weaknesses.
- Produces structured issue and evidence objects.

### Agent 2 — Legal Research
- Maintains a research trajectory rather than performing a fixed search sequence.
- Judges whether previous results actually answer the issue.
- Chooses the next search type and reformulates the query.
- Can use the local verified repository or live legal-web search.
- Decides when research coverage is sufficient, subject to a safety ceiling.

### Agent 3 — Advocate
- Receives the complete Agent 1 + Agent 2 context.
- Constructs a theory of the case.
- Generates an adversarial attack as opposing counsel.
- Assesses whether the attack is fatal, significant, minor, or survivable.
- Rebuilds the theory when its own attack exposes a material weakness.

### Agent 4 — Adjudicator & Reporting
- Audits citation provenance.
- Evaluates argument, evidence, and precedent strength.
- Attributes root cause to a specific upstream agent.
- Emits `PASS` or `REVISE` with a concrete remediation instruction.
- Routes only the targeted stage when revision is necessary.
- Compiles the final report from the complete case trajectory, not a generic template.

## 3. State Invariant

The system maintains one canonical LangGraph state per research session:

- case identity and objective
- requested execution strategy
- Agent 1 structured output
- Agent 2 research findings + trajectory
- Agent 3 theory + attack + self-assessment
- Agent 4 merits/citation audit
- revision history
- execution history
- final report

Repeated agent executions store the output from **that exact invocation**, so the database contains a real trajectory rather than repeated copies of the final state.

## 4. Evaluation

The evaluation harness is inspired by trajectory-oriented **Agent-as-a-Judge** methodology, but the metrics are adapted to LexIntel's legal workflow rather than claiming to reproduce the paper's benchmark.

Metrics include:

- Requirements Met — Independent
- Requirements Met — Dependency-aware
- Task Solve Rate
- Self-Termination
- Trajectory Quality
- Retrieval Precision
- Retrieval Recall
- Retrieval F1
- Citation Validity
- Citation Grounding
- Agent Reliability
- Latency

Run:

```bash
cd backend
python -m app.evaluation.evaluator
```

Results are written to:

```text
backend/app/evaluation/eval_results.json
```

The frontend Evaluation page reads the current four-agent metrics directly.

## 5. LLM Reliability

Remote LLM failures are **not silently converted to fake mock answers** by default.

`.env.example` contains:

```text
LLM_PROVIDER=gemini
LLM_MODEL=<your-supported-gemini-model>
GEMINI_API_KEY=<your-key>
ALLOW_MOCK_FALLBACK=False
LLM_MAX_RETRIES=2
LLM_TIMEOUT_SECONDS=50
```

For deterministic offline tests only:

```text
LLM_PROVIDER=mock
```

API keys are sent to Gemini through a request header rather than a URL so they are not accidentally exposed through request logging.

## 6. Setup

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## 7. Tests

The repository contains tests for:

- four-agent routing
- Agent 3 execution
- bounded revision routing
- structured agent outputs
- API behavior
- RAG retrieval
- citation validation
- model relationships
- security paths
- evaluation API

Run:

```bash
python -m pytest -v
```

## 8. Important Security Step

Do **not** commit `.env` or API keys. Use `.env.example` as the template. If a Gemini key was previously exposed in logs or screenshots, revoke it and create a replacement.

## 9. Documentation

- `docs/architecture-v2.md` — current orchestration design
- `docs/evaluation-v2.md` — evaluation methodology
- `docs/architecture.md` — broader system diagrams
- `docs/api.md` — API reference
- `docs/demo.md` — demonstration flow
- `PROJECT_STATUS.md` — implementation and verification status


## Gemini production architecture (updated)
- Four-agent Full Litigation only: Case Intake → Legal Research → Advocate → Adjudicator/Reporting.
- Gemini 3.8 Flash / Gemini 3.1 Flash-Lite with structured JSON/Pydantic outputs, configurable thinking level.
- Agentic RAG uses adaptive research decisions with a 3-step hard ceiling and early stopping based on knowledge sufficiency.
- Advocate uses bounded Defender/Attacker self-play and revises only when the attack is material.
- Adjudicator never supplies fake numeric evaluation scores; the deterministic evaluation engine calculates run metrics from the observed trajectory, evidence provenance and citation audit.
- Every run persists dynamic metrics including task solve rate, dependency-aware requirements, self-termination, evidence coverage/alignment, authority coverage, citation validity, research sufficiency, steps, LLM calls, tool calls, retries, latency and revisions.
- Revision exhaustion results in INCONCLUSIVE, not a false PASS.
