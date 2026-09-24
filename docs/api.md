# LexIntel AI: REST API Reference

The LexIntel AI backend is powered by FastAPI, exposing type-safe REST endpoints documented automatically via OpenAPI / Swagger at `http://127.0.0.1:8000/docs`.

---

## 1. Authentication & Users
- **`POST /api/auth/register`**: Register a new counsel user account.
  - Body: `{"email": "counsel@firm.com", "password": "secure_password", "full_name": "Counsel Name", "role": "lawyer"}`
- **`POST /api/auth/token`**: OAuth2 password grant endpoint to obtain JWT bearer token.
  - Form Data: `username`, `password`
  - Response: `{"access_token": "<jwt>", "token_type": "bearer"}`
- **`GET /api/auth/me`**: Return authenticated user profile.

---

## 2. Cases Management
- **`GET /api/cases`**: List all legal matters accessible to counsel.
- **`POST /api/cases`**: Create a new legal matter.
  - Body: `{"title": "...", "description": "...", "client_name": "...", "case_type": "civil_litigation", "legal_domain": "Commercial Contracts", "jurisdiction": "US Federal"}`
- **`GET /api/cases/{id}`**: Retrieve detailed case profile, associated exhibits, and prior research runs.
- **`PUT /api/cases/{id}`**: Update case metadata or status.
- **`DELETE /api/cases/{id}`**: Soft-delete or archive a case.

---

## 3. Document Ingestion & Verification
- **`POST /api/documents/upload`**: Upload and process an evidentiary document.
  - Security Enforced: Filename sanitization, extension verification (`.pdf`, `.docx`, `.txt`, `.md`, `.json`), MIME check, 15MB file size limit.
  - Form Data: `case_id`, `file`
  - Returns: Parsed document metadata, chunk count, and ingestion status.
- **`GET /api/documents/{id}`**: Retrieve document details and parsed content preview.

---

## 4. Multi-Agent Research Execution
- **`POST /api/research/start`**: Launch autonomous LangGraph multi-agent analysis.
  - Body:
    ```json
    {
      "case_id": "uuid-string",
      "objective": "Evaluate breach of contract liability and liquidated damages enforceability",
      "execution_strategy": "full_litigation",
      "preferred_jurisdiction": "US Federal / Delaware"
    }
    ```
  - Response: Session ID, status (`completed`), and array of step execution logs.
- **`GET /api/research/{session_id}`**: Get status, node execution steps, and progress.

---

## 5. Intelligence Reports & Dossiers
- **`GET /api/reports/{id}`**: Retrieve complete 18-section intelligence dossier.
  - Includes: `sections` dictionary, `citations` array with tri-tier grounding badges, `executive_summary`, and `created_at`.
- **`GET /api/reports/case/{case_id}`**: List all historical dossiers generated for a case.

---

## 6. Evaluation & Benchmarks
- **`GET /api/evaluation/results`**: Retrieve pre-computed benchmark results across all 4 test scenarios, agent reliability metrics, and citation validity.
- **`POST /api/evaluation/run`**: Trigger real-time execution of the benchmark suite and return fresh scores.

---

## 7. System Health
- **`GET /api/health`**: Health check returning system status, active LLM provider (`mock`, `ollama`, `openai`, `gemini`), and version.\n