# LexIntel AI: Setup & Operation Guide

## Prerequisites

* Python 3.10+ (tested on Python 3.13)
* Node.js 18+ (tested on Node v24)
* npm 9+

---

## 1. Backend Service Setup

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* **Swagger API UI**: `http://localhost:8000/docs`
* **Health Check**: `http://localhost:8000/api/health`

---

## 2. Frontend Application Setup

```bash
cd frontend
npm install
npm run dev
```

* **Web Application**: `http://localhost:5173`

---

## 3. Automated Testing Suite

Execute the full suite of 17 automated tests covering agents, API endpoints, RAG retrieval, citation verification, and workflow state machines:

```bash
# From repository root
python -m pytest -v
```

---

## 4. Benchmark Evaluation Suite

Run the quantitative benchmark evaluation harness to evaluate legal retrieval precision, agent completion, citation validity, and latency:

```bash
python -m app.evaluation.evaluator
```

Benchmark output is exported to `backend/app/evaluation/eval_results.json`.

---

## 5. Multi-Scenario Live Verification

To verify that all 3 seeded legal scenarios execute cleanly through the live HTTP API:

```bash
python scratch/verify_all_scenarios.py
```

---

## 6. Docker Deployment

To launch the complete application stack (Backend + Frontend) via Docker:

```bash
docker-compose up --build
```
