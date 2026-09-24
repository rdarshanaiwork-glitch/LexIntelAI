import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import init_db

@pytest.fixture(autouse=True)
def setup():
    init_db()

def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "LexIntel AI" in data["app_name"]

def test_cases_and_research_flow():
    with TestClient(app) as client:
        # 1. List cases (triggers seeding)
        res = client.get("/api/cases")
        assert res.status_code == 200
        cases = res.json()
        assert len(cases) >= 1
        case_id = cases[0]["id"]

        # 2. Get case by id
        res_case = client.get(f"/api/cases/{case_id}")
        assert res_case.status_code == 200
        assert res_case.json()["id"] == case_id

        # 3. Start research session
        res_start = client.post("/api/research/start", json={
            "case_id": case_id,
            "objective": "Assess enforceability of liquidated damages under Restatement 356."
        })
        assert res_start.status_code == 201
        session_data = res_start.json()
        assert session_data["status"] == "completed"
        assert len(session_data["agent_executions"]) >= 4
        assert len(session_data["reports"]) >= 1

        report_id = session_data["reports"][0]["id"]
        res_rep = client.get(f"/api/reports/{report_id}")
        assert res_rep.status_code == 200
        report_json = res_rep.json()
        assert "title" in report_json
        assert len(report_json["citations"]) > 0