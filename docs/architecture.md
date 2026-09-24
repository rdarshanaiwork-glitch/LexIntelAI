# LexIntel AI Architecture

## Runtime architecture

```mermaid
flowchart TD
    U[User / Case] --> A1[Agent 1: Case Intake]
    A1 --> A2[Agent 2: Legal Research]
    A2 -->|full_litigation| A3[Agent 3: Advocate]
    A2 -->|simple_inquiry| A4[Agent 4: Adjudicator & Reporting]
    A3 --> A4
    A4 -->|PASS| R[Final Legal Intelligence Report]
    A4 -->|REVISE: intake| A1
    A4 -->|REVISE: research| A2
    A4 -->|REVISE: advocate| A3
```

## Agent 2 decision loop

```mermaid
flowchart LR
    Q[Legal Issue] --> D[LLM judges coverage]
    D --> S[Choose next search]
    S --> T[Legal retrieval tool]
    T --> D
    D -->|coverage sufficient| F[Structured research package]
```

## Agent 3 deliberation loop

```mermaid
flowchart LR
    R[Research package] --> B[Build case theory]
    B --> O[Opposing counsel attack]
    O --> M[Materiality assessment]
    M -->|material weakness| B
    M -->|survivable| A[Finalize advocacy package]
```

## Agent 4 quality gate

```mermaid
flowchart LR
    T[Complete trajectory] --> C[Citation audit]
    C --> J[Merits + evidence + precedent evaluation]
    J --> G[Root-cause quality gate]
    G -->|PASS| P[Report compilation]
    G -->|REVISE| X[Targeted upstream repair]
```

The graph is intentionally deterministic at the orchestration layer. The LLM makes decisions inside each agent about research strategy, argument construction, adversarial materiality, and quality-gate remediation; LangGraph controls the safe execution topology and revision ceiling.
