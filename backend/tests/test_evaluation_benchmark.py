"""Tests for evaluation benchmarking runner and GET /api/eval endpoint."""

import os
from fastapi.testclient import TestClient

from app.main import app
from eval.run_eval import (
    calculate_flesch_kincaid_grade,
    check_standard_code,
    count_syllables,
    run_full_eval,
)

client = TestClient(app)


def test_flesch_kincaid_grade_level():
    """Verify Flesch-Kincaid grade level calculation on elementary sentences."""
    simple = "Maya has two peach pies. She gives one to her friend Leo. How many are left?"
    fk = calculate_flesch_kincaid_grade(simple)
    assert 1.0 <= fk <= 7.0, f"Expected elementary grade level, got {fk}"

    syllables = count_syllables("fractions")
    assert syllables == 2


def test_check_standard_code():
    """Verify standard code validation across topics and grades."""
    assert check_standard_code("MGSE5.NF.1", "fractions", 5) is True
    assert check_standard_code("MGSE6.RP.3", "ratios", 6) is True
    assert check_standard_code("MGSE5.NBT.7", "decimals", 5) is True
    # Wrong grade
    assert check_standard_code("MGSE6.RP.3", "ratios", 5) is False
    # Wrong topic
    assert check_standard_code("MGSE5.NF.1", "geometry", 5) is False


def test_get_api_eval_summary():
    """Verify GET /api/eval returns the 2-model x 2-prompt summary."""
    response = client.get("/api/eval")
    assert response.status_code == 200, response.text
    data = response.json()

    assert "total_evaluated" in data
    assert "models_evaluated" in data
    assert len(data["models_evaluated"]) == 2
    assert "prompts_evaluated" in data
    assert len(data["prompts_evaluated"]) == 2
    assert "configurations" in data
    assert len(data["configurations"]) == 4

    for cfg in data["configurations"]:
        assert "model" in cfg
        assert "prompt_version" in cfg
        assert "schema_validity_percent" in cfg
        assert "math_accuracy_percent" in cfg
        assert "standard_code_correctness_percent" in cfg
        assert "avg_readability_grade" in cfg
        assert "avg_latency_ms" in cfg

    assert "conclusion" in data
    assert len(data["conclusion"]) > 20
