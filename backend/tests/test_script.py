"""Tests for POST /api/script endpoint."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_post_api_script_returns_6_slides():
    """Verify POST /api/script returns exactly 6 validated slides for a topic."""
    response = client.post(
        "/api/script",
        json={"grade": 5, "topic": "fractions"},
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["topic"] == "fractions"
    assert data["grade"] == 5
    assert data["title"]
    assert data["standard_code"]
    assert len(data["slides"]) == 6

    for idx, slide in enumerate(data["slides"]):
        assert slide["slide_number"] == idx + 1
        assert slide["title"]
        assert len(slide["bullets"]) >= 2
        assert slide["narration"]
        assert slide["visual_component"] in ["FractionBar", "NumberLine", "ShapeDiagram", "TopicGraphic"]
        assert slide["duration_seconds"] >= 3


def test_post_api_script_all_topics():
    """Verify script generation across all 6 topics for Grade 6."""
    topics = ["fractions", "decimals", "ratios", "geometry", "factors_multiples", "integers"]
    for t in topics:
        res = client.post("/api/script", json={"grade": 6, "topic": t})
        assert res.status_code == 200
        d = res.json()
        assert len(d["slides"]) == 6
        assert d["topic"] == t



def test_post_api_script_caching():
    """Verify POST /api/script caches the generated script."""
    r1 = client.post("/api/script", json={"grade": 5, "topic": "geometry"})
    assert r1.status_code == 200

    r2 = client.post("/api/script", json={"grade": 5, "topic": "geometry"})
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["cached"] is True
    assert len(d2["slides"]) == 6


def test_post_api_script_invalid_grade_rejected():
    """Verify grades other than 5 and 6 are rejected by Pydantic."""
    res = client.post("/api/script", json={"grade": 4, "topic": "fractions"})
    assert res.status_code == 422
