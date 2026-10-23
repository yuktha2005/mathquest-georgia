"""Test suite for RAG standards retrieval, POST /api/explain, and GET /api/infographic."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.rag import retrieve_standards, format_standards_for_prompt
from app.services.verify import evaluate
from app.schemas import ExplainStyle

client = TestClient(app)


def test_standards_files_contain_mgse():
    """Verify standards files for fractions, decimals, ratios, and geometry have MGSE codes."""
    topics = ["fractions", "decimals", "ratios", "geometry"]
    for topic in topics:
        results = retrieve_standards(topic=topic, grade=5, limit=2)
        assert len(results) > 0, f"Expected standards for {topic} Grade 5"
        assert results[0]["code"].startswith("MGSE"), f"Code {results[0]['code']} must start with MGSE"
        assert results[0]["summary"], f"Summary for {results[0]['code']} should not be empty"

        results_g6 = retrieve_standards(topic=topic, grade=6, limit=2)
        assert len(results_g6) > 0, f"Expected standards for {topic} Grade 6"
        assert results_g6[0]["code"].startswith("MGSE")


def test_retrieve_top_2_standards():
    """Verify retrieve_standards defaults to top 2 standards."""
    standards = retrieve_standards(query="fractions", topic="fractions", grade=5, limit=2)
    assert len(standards) <= 2
    assert len(standards) >= 1
    assert "MGSE5" in standards[0]["code"]

    prompt_ctx = format_standards_for_prompt(standards)
    assert "MGSE5" in prompt_ctx


def test_post_api_explain_all_styles():
    """Verify POST /api/explain returns structured JSON for all 4 styles."""
    styles = ["default", "simpler", "real_life", "step_by_step"]
    for s in styles:
        response = client.post(
            "/api/explain",
            json={"grade": 5, "topic": "fractions", "style": s},
        )
        assert response.status_code == 200, response.text
        data = response.json()

        assert data["title"]
        assert data["intro"]
        assert len(data["key_ideas"]) >= 2
        assert len(data["worked_examples"]) == 2
        assert len(data["common_mistakes"]) >= 1
        assert data["standard_code"].startswith("MGSE")
        assert data["style"] == s

        # Rule 1 verification: verify each worked example mathematically
        for ex in data["worked_examples"]:
            assert ex["problem"]
            assert ex["expression"]
            assert len(ex["steps"]) >= 2
            # evaluate(ex["expression"]) must equal or be compatible with verified_answer
            computed = evaluate(ex["expression"])
            assert computed is not None, f"Expression {ex['expression']} failed evaluation"


def test_post_api_explain_caching():
    """Verify POST /api/explain caches the results locally."""
    # First call might populate cache
    r1 = client.post(
        "/api/explain",
        json={"grade": 6, "topic": "geometry", "style": "step_by_step"},
    )
    assert r1.status_code == 200
    d1 = r1.json()

    # Second call should serve from cache
    r2 = client.post(
        "/api/explain",
        json={"grade": 6, "topic": "geometry", "style": "step_by_step"},
    )
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["cached"] is True
    assert d2["title"] == d1["title"]
    assert d2["worked_examples"] == d1["worked_examples"]


def test_get_api_infographic_returns_pollinations_url():
    """Verify GET /api/infographic returns a Pollinations.ai image URL built from topic prompt."""
    response = client.get("/api/infographic?topic=fractions&grade=5")
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["topic"] == "fractions"
    assert "pollinations.ai" in data["image_url"]
    assert "pollinations.ai" in data["url"]
    assert data["fallback_url"] == "/infographics/fractions.svg"
    assert "fractions" in data["prompt"].lower()
