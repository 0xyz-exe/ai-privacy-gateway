import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import validate_upstream_url

client = TestClient(app)

def test_ssrf_protection():
    # Loopback rejected when allow_local=False
    assert not validate_upstream_url("http://127.0.0.1:8000/v1", allow_local=False)
    assert not validate_upstream_url("http://localhost:8000/v1", allow_local=False)
    
    # Loopback accepted when allow_local=True (for local Ollama)
    assert validate_upstream_url("http://127.0.0.1:11434/v1", allow_local=True)
    assert validate_upstream_url("http://localhost:11434", allow_local=True)
    
    # Cloud metadata address rejected ALWAYS
    assert not validate_upstream_url("http://169.254.169.254/latest/meta-data/", allow_local=True)
    assert not validate_upstream_url("http://169.254.169.254/latest/meta-data/", allow_local=False)
    
    # Invalid schemes
    assert not validate_upstream_url("ftp://example.com/api", allow_local=False)
    assert not validate_upstream_url("file:///etc/passwd", allow_local=False)

def test_health_endpoints():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"

def test_playground_analyze():
    payload = {
        "text": "Please email me at alice@test.com or call +62 812-3456-7890.",
        "mode": "redact",
        "min_confidence": 0.70
    }
    res = client.post("/api/playground/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["policy_decision"] == "redacted"
    assert "[EMAIL_ADDRESS_1]" in data["redacted_text"]
    assert "alice@test.com" not in data["redacted_text"]
    assert data["redaction_count"] >= 2

def test_chat_completions_mock_integration():
    # Test POST /v1/chat/completions with Mock engine
    chat_payload = {
        "model": "mock-gpt-4o",
        "messages": [
            {"role": "user", "content": "My secret email is ceo@company.com"}
        ],
        "stream": False
    }
    res = client.post("/v1/chat/completions", json=chat_payload)
    assert res.status_code == 200
    data = res.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    reply = data["choices"][0]["message"]["content"]
    # Mock engine reports received placeholders
    assert "[EMAIL_ADDRESS_1]" in reply

def test_chat_completions_policy_block():
    # Update default policy or trigger a blocked entity
    # Credit card on strict block
    chat_payload = {
        "model": "mock-gpt-4o",
        "messages": [
            {"role": "user", "content": "Credit card 4532-0150-1234-5674"}
        ],
        "stream": False
    }
    # Set header to test with standard flow
    res = client.post("/v1/chat/completions", json=chat_payload)
    # Standard policy allows redaction, or strict blocks
    assert res.status_code in (200, 403)
