"""Unit tests for slowapi rate limiting, input validation, and global error handlers."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.limiter import limiter


@pytest.fixture
def client():
    return TestClient(app)


def test_input_validation_invalid_topic(client):
    """Verify POST /api/question rejects unsupported math topics with structured 422."""
    res = client.post("/api/question", json={"grade": 5, "topic": "quantum_physics", "tier": "medium"})
    assert res.status_code == 422
    data = res.json()
    assert data["error"] == "Validation Error"
    assert "Oops!" in data["message"]
    assert any("topic" in err["field"] for err in data["details"])


def test_input_validation_invalid_grade(client):
    """Verify POST /api/question rejects grades other than 5 or 6."""
    res = client.post("/api/question", json={"grade": 3, "topic": "fractions", "tier": "medium"})
    assert res.status_code == 422
    data = res.json()
    assert data["error"] == "Validation Error"
    assert any("grade" in err["field"] for err in data["details"])


def test_input_validation_invalid_tier(client):
    """Verify POST /api/question rejects non-existent tiers."""
    res = client.post("/api/question", json={"grade": 5, "topic": "fractions", "tier": "godmode"})
    assert res.status_code == 422
    data = res.json()
    assert data["error"] == "Validation Error"
    assert any("tier" in err["field"] for err in data["details"])


def test_input_validation_batch_count_bounds(client):
    """Verify count parameter is strictly bounded between 1 and 10."""
    res_high = client.post("/api/question", json={"grade": 5, "topic": "fractions", "tier": "medium", "count": 25})
    assert res_high.status_code == 422
    assert any("count" in err["field"] for err in res_high.json()["details"])

    res_zero = client.post("/api/question", json={"grade": 5, "topic": "fractions", "tier": "medium", "count": 0})
    assert res_zero.status_code == 422
    assert any("count" in err["field"] for err in res_zero.json()["details"])


def test_input_validation_answer_hints_bound(client):
    """Verify hints_used on /api/answer must be between 0 and 3."""
    res = client.post(
        "/api/answer",
        json={
            "question_id": "test-123",
            "selected_option_id": "A",
            "hints_used": 5,  # Exceeds max 3 hints
        },
    )
    assert res.status_code == 422
    data = res.json()
    assert any("hints_used" in err["field"] for err in data["details"])


def test_infographic_invalid_topic_400(client):
    """Verify GET /api/infographic returns 400 for unknown topic."""
    res = client.get("/api/infographic?topic=algebra")
    assert res.status_code == 400
    data = res.json()
    assert "Invalid topic" in data["message"]


def test_not_found_global_error_handler(client):
    """Verify 404 responses are formatted cleanly."""
    res = client.get("/api/non_existent_route_404")
    assert res.status_code == 404
    data = res.json()
    assert data["error"] == "HTTP Error"
    assert data["status_code"] == 404


def test_unhandled_exception_global_handler(monkeypatch):
    """Verify unexpected internal errors are safely caught with 500 without leaking secrets."""
    from app.routers import question

    def faulty_pipeline(*args, **kwargs):
        raise RuntimeError("SecretDatabaseKeyException: internal database connection failed!")

    monkeypatch.setattr(question, "build_question_pipeline", faulty_pipeline)

    test_client = TestClient(app, raise_server_exceptions=False)
    res = test_client.post("/api/question", json={"grade": 5, "topic": "fractions", "tier": "medium"})
    assert res.status_code == 500
    data = res.json()
    assert data["error"] == "Internal Server Error"
    # Never leaks internal exception details to client
    assert "SecretDatabaseKeyException" not in str(data)
    assert "Our math engine encountered an unexpected hiccup" in data["message"]


def test_rate_limiting_exceeded_handler(monkeypatch):
    """Verify rate limiter triggers 429 when limits are reached."""
    # Temporarily enable rate limiter for this test
    original_enabled = limiter.enabled
    limiter.enabled = True
    try:
        # Create a test route with 2/minute limit
        @app.get("/api/test-rate-limit")
        @limiter.limit("2/minute")
        def limited_route(request: pytest.importorskip("fastapi").Request):
            return {"status": "ok"}

        test_client = TestClient(app)
        r1 = test_client.get("/api/test-rate-limit")
        assert r1.status_code == 200
        r2 = test_client.get("/api/test-rate-limit")
        assert r2.status_code == 200
        r3 = test_client.get("/api/test-rate-limit")
        assert r3.status_code == 429
        data = r3.json()
        assert data["error"] == "Too Many Requests"
        assert "math explorer" in data["message"]
    finally:
        limiter.enabled = original_enabled
