"""Unit and integration tests for Curriculum Packs and Loader Service."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import CurriculumPack, Tier
from app.services.curriculum import (
    CurriculumPackNotFoundError,
    curriculum_service,
    get_curriculum_pack,
    get_topic_config,
    list_curriculum_packs,
)

client = TestClient(app)


def test_load_georgia_g5_pack() -> None:
    """Test loading and validating the Georgia Grade 5 curriculum pack."""
    pack = get_curriculum_pack("georgia", 5)
    assert pack.board == "georgia"
    assert pack.grade == 5
    assert pack.verified is True
    assert len(pack.topics) == 4

    topic_ids = [t.id for t in pack.topics]
    assert "fractions" in topic_ids
    assert "decimals" in topic_ids
    assert "ratios" in topic_ids
    assert "geometry" in topic_ids

    fractions = pack.get_topic("fractions")
    assert fractions is not None
    assert fractions.standard_code == "MGSE5.NF.1"
    assert "easy" in fractions.tier_rules
    assert "medium" in fractions.tier_rules
    assert "hard" in fractions.tier_rules
    assert fractions.tier_rules["easy"].tier == Tier.EASY


def test_load_georgia_g6_pack() -> None:
    """Test loading and validating the Georgia Grade 6 curriculum pack."""
    pack = get_curriculum_pack("georgia", 6)
    assert pack.board == "georgia"
    assert pack.grade == 6
    assert pack.verified is True
    assert len(pack.topics) == 4

    fractions = pack.get_topic("fractions")
    assert fractions is not None
    assert fractions.standard_code == "MGSE6.NS.1"

    ratios = pack.get_topic("ratios")
    assert ratios is not None
    assert ratios.standard_code == "MGSE6.RP.3"


def test_load_cbse_g6_pack() -> None:
    """Test loading and validating the CBSE Class 6 Ganita Prakash pack."""
    pack = get_curriculum_pack("cbse", 6)
    assert pack.board == "cbse"
    assert pack.grade == 6
    assert "Ganita Prakash" in pack.board_name
    assert pack.verified is True
    assert len(pack.topics) == 6

    topic_ids = [t.id for t in pack.topics]
    expected_topics = ["factors_multiples", "fractions", "decimals", "integers", "ratios", "geometry"]
    for expected in expected_topics:
        assert expected in topic_ids

    factors = pack.get_topic("factors_multiples")
    assert factors is not None
    assert factors.standard_code == "CBSE6.MATH.03"
    assert "Playing with Numbers" in factors.standard_title


def test_curriculum_pack_not_found() -> None:
    """Test loading non-existent curriculum pack raises CurriculumPackNotFoundError."""
    with pytest.raises(CurriculumPackNotFoundError):
        curriculum_service.load_pack("mars_board", 5)

    with pytest.raises(CurriculumPackNotFoundError):
        curriculum_service.load_pack("georgia", 12)


def test_list_curriculum_packs() -> None:
    """Test listing all packs returns at least georgia-g5, georgia-g6, cbse-g6."""
    packs = list_curriculum_packs()
    assert len(packs) >= 3

    pack_keys = [(p.board, p.grade) for p in packs]
    assert ("georgia", 5) in pack_keys
    assert ("georgia", 6) in pack_keys
    assert ("cbse", 6) in pack_keys


def test_get_topic_config_and_tier_rules() -> None:
    """Test topic config and tier rule retrieval helpers."""
    topic = get_topic_config("cbse", 6, "factors_multiples")
    assert topic is not None
    assert topic.standard_code == "CBSE6.MATH.03"

    non_topic = get_topic_config("georgia", 5, "quantum_physics")
    assert non_topic is None

    rule_easy = curriculum_service.get_tier_rule("georgia", 5, "fractions", Tier.EASY)
    assert rule_easy is not None
    assert rule_easy.tier == Tier.EASY

    rule_hard = curriculum_service.get_tier_rule("cbse", 6, "factors_multiples", "hard")
    assert rule_hard is not None
    assert rule_hard.tier == Tier.HARD


def test_api_get_curriculum_packs() -> None:
    """Test GET /api/curriculum/packs endpoint."""
    response = client.get("/api/curriculum/packs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    boards = [item["board"] for item in data]
    assert "georgia" in boards
    assert "cbse" in boards


def test_api_get_curriculum_pack_by_board_and_grade() -> None:
    """Test GET /api/curriculum/pack/{board}/{grade} endpoint."""
    # Valid Georgia Grade 5
    res_geo = client.get("/api/curriculum/pack/georgia/5")
    assert res_geo.status_code == 200
    assert res_geo.json()["board"] == "georgia"
    assert res_geo.json()["grade"] == 5

    # Valid CBSE Grade 6
    res_cbse = client.get("/api/curriculum/pack/cbse/6")
    assert res_cbse.status_code == 200
    assert res_cbse.json()["board"] == "cbse"
    assert res_cbse.json()["grade"] == 6

    # 404 for unknown pack
    res_404 = client.get("/api/curriculum/pack/unknown_board/99")
    assert res_404.status_code == 404


def test_api_get_topics_for_board_and_grade() -> None:
    """Test GET /api/curriculum/topics/{board}/{grade} endpoint."""
    res = client.get("/api/curriculum/topics/cbse/6")
    assert res.status_code == 200
    topics = res.json()
    assert isinstance(topics, list)
    assert len(topics) == 6
    assert topics[0]["id"] == "factors_multiples"

    res_404 = client.get("/api/curriculum/topics/non_existent/1")
    assert res_404.status_code == 404


def test_question_generation_with_cbse_board() -> None:
    """Test /api/question endpoint with board='cbse'."""
    payload = {
        "board": "cbse",
        "grade": 6,
        "topic": "factors_multiples",
        "tier": "easy",
        "count": 1,
    }
    response = client.post("/api/question", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["board"] == "cbse"
    assert data["grade"] == 6
    assert len(data["options"]) >= 2
    assert data["correct_option_id"] in [opt["id"] for opt in data["options"]]
