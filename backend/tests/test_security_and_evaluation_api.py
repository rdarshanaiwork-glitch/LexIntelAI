import pytest
import io
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.services.doc_service import sanitize_filename

client = TestClient(app)

def get_auth_token():
    test_email = f"counsel_{uuid.uuid4().hex[:6]}@lexintel.ai"
    reg_res = client.post("/api/auth/register", json={
        "email": test_email,
        "password": "password123",
        "full_name": "Test Lead Counsel"
    })
    if reg_res.status_code == 201:
        return reg_res.json()["access_token"]
    login_res = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "password123"
    })
    return login_res.json().get("access_token")

def test_evaluation_api_results():
    response = client.get("/api/evaluation/results")
    assert response.status_code == 200
    data = response.json()
    assert "workflow_success_rate" in data
    assert "retrieval_precision" in data
    assert "scenario_breakdown" in data
    assert "architecture" in data

def test_evaluation_api_run():
    response = client.post("/api/evaluation/run")
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_success_rate"] == 1.0
    assert data["requirements_met_dependency_aware"] >= 0.75

def test_filename_sanitization():
    unsafe_name = "../../etc/passwd"
    clean = sanitize_filename(unsafe_name)
    assert ".." not in clean
    assert "/" not in clean
    assert "\\" not in clean
    assert clean == "passwd"

def test_upload_invalid_extension():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Try uploading an unauthorized file type (.exe)
    file_payload = {"file": ("malicious.exe", io.BytesIO(b"binary payload"), "application/x-msdownload")}
    response = client.post("/api/documents/upload", data={"case_id": "invalid-case"}, files=file_payload, headers=headers)
    assert response.status_code == 400
    assert "extension" in response.json()["detail"].lower()

def test_missing_case_404():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = client.get("/api/cases/non-existent-case-id-12345", headers=headers)
    assert response.status_code == 404

def test_auth_failure_path():
    response = client.post("/api/auth/login", json={"email": "nonexistent@lexintel.ai", "password": "wrongpassword"})
    assert response.status_code == 401
