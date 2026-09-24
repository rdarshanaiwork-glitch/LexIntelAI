# Windows Quick Start

## Backend

Open PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy the root environment template:

```powershell
Copy-Item ..\.env.example ..\.env
```

Edit `..\.env` and set your own Gemini key/model.

Start:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Frontend

In a second PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Verification

Run backend tests:

```powershell
python -m pytest -v
```

Run evaluation:

```powershell
cd backend
python -m app.evaluation.evaluator
```

Then refresh the Evaluation page.

## Recommended demo mode

Use **Full Litigation** for the strongest demonstration because it visibly executes:

`Agent 1 → Agent 2 → Agent 3 → Agent 4`

Agent 3 should show a case theory, opposing attack, and materiality self-assessment. Agent 4 should show a merits evaluation, citation audit, root-cause decision, and PASS/REVISE gate.
