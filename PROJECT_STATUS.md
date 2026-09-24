# LexIntel AI — Project Status

## Orchestration repaired

- 4-agent architecture is now the canonical runtime architecture.
- Full litigation always executes Agent 1 → Agent 2 → Agent 3 → Agent 4.
- Simple inquiry intentionally executes Agent 1 → Agent 2 → Agent 4.
- Agent 1 cannot override the user-selected graph strategy.
- Agent 4 revision decisions are targeted and bounded.
- Repeated agent executions preserve their own output payloads.

## Context quality repaired

- Removed the old 400/500-character handoff pattern from Agents 2–4.
- Added structured context compaction that preserves beginning and end of large state objects.
- Agent 4 receives case facts, issues, research, advocacy, citation audit and revision history.
- Final report fields are enriched from actual upstream trajectory data.

## LLM reliability repaired

- Gemini API keys are sent in a header, not in a URL.
- Remote LLM failures no longer silently become fake mock results unless `ALLOW_MOCK_FALLBACK=True` is explicitly enabled.
- Retries are bounded by configuration.

## Evaluation repaired

- Removed all 10-agent assumptions.
- Added trajectory/dependency-aware requirements metrics.
- Added retrieval precision/recall/F1.
- Added citation validity/grounding.
- Added self-termination and task-solve metrics.

## Verification performed in this build environment

- Python syntax compilation completed for modified backend modules.
- TypeScript type-check (`tsc --noEmit`) completed successfully.
- Full pytest execution could not be executed in this isolated environment because the runtime image does not contain the project's Python dependencies and has no external package-network access. The project retains its requirements file for local installation.
- Frontend Vite production build could not be reproduced in this isolated environment because the archived `node_modules` lacks Rollup's platform-specific optional binary. TypeScript compilation itself passes.

## Before first run

1. Copy `.env.example` to `.env`.
2. Set `LLM_PROVIDER=gemini` and your own `GEMINI_API_KEY`.
3. Set a supported Gemini model in `LLM_MODEL`.
4. Keep `ALLOW_MOCK_FALLBACK=False` for real evaluation.
5. Install backend dependencies with `pip install -r backend/requirements.txt`.
6. Install frontend dependencies with `npm install` inside `frontend/`.
7. Run the backend and frontend using the commands in `README.md`.
