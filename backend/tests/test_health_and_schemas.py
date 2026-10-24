"""Unit and integration tests for health endpoint and Pydantic v2 schemas."""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas import (
    AnswerResult,
    AnswerSubmission,
    CurriculumPack,
    HealthResponse,
    MathTopic,
    Option,
    Question,
    QuestionTemplate,
    QuestionType,
    Tier,
    TierRule,
    TopicConfig,
)

client = TestClient(app)


def test_health_endpoint() -> None:
    """Test GET /health returns 200 OK with expected schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    health = HealthResponse.model_validate(data)
    assert health.status == "ok"
    assert "MathQuest" in health.app


def test_cors_headers() -> None:
    """Test CORS headers are returned for configured origin."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_tier_enum_values() -> None:
    """Test Tier enum supports easy, medium, and hard."""
    assert Tier.EASY.value == "easy"
    assert Tier.MEDIUM.value == "medium"
    assert Tier.HARD.value == "hard"
    assert list(Tier) == [Tier.EASY, Tier.MEDIUM, Tier.HARD]


def test_option_schema() -> None:
    """Test Option schema serialization and optional misconception tag."""
    opt_correct = Option(id="A", text="3/4")
    assert opt_correct.misconception_tag is None

    opt_distractor = Option(
        id="B",
        text="2/3",
        misconception_tag="inverted_fraction",
    )
    assert opt_distractor.misconception_tag == "inverted_fraction"


def test_question_schema_valid() -> None:
    """Test valid Question instance passes schema validation."""
    question = Question(
        id="q-001",
        topic="fractions",
        grade=5,
        tier=Tier.EASY,
        stem="What is 1/4 + 2/4?",
        expression="1/4 + 2/4",
        options=[
            Option(id="A", text="3/4"),
            Option(id="B", text="3/8", misconception_tag="add_denominators"),
        ],
        correct_option_id="A",
        explanation="Add the numerators 1 + 2 = 3 over the common denominator 4 to get 3/4.",
        standard_code="MGSE5.NF.1",
    )
    assert question.id == "q-001"
    assert question.grade == 5
    assert len(question.options) == 2


def test_question_schema_invalid_correct_option() -> None:
    """Test Question validator rejects correct_option_id not in options."""
    with pytest.raises(ValidationError) as exc_info:
        Question(
            id="q-invalid",
            topic="fractions",
            grade=5,
            tier=Tier.EASY,
            stem="Test stem",
            expression="1 + 1",
            options=[
                Option(id="A", text="2"),
                Option(id="B", text="3"),
            ],
            correct_option_id="Z",  # Not in options
            explanation="Test explanation",
            standard_code="MGSE5.OA.1",
        )
    assert "correct_option_id" in str(exc_info.value)


def test_question_template_schema() -> None:
    """Test QuestionTemplate returned by LLM prior to verification."""
    template = QuestionTemplate(
        stem="Maya has 2.5 meters of ribbon. She cuts 1.2 meters. How much ribbon remains?",
        expression="2.5 - 1.2",
        standard_code="MGSE5.NBT.7",
        topic="decimals",
        tier=Tier.MEDIUM,
    )
    assert template.tier == Tier.MEDIUM
    assert template.topic == "decimals"


def test_answer_submission_and_result() -> None:
    """Test AnswerSubmission and AnswerResult models."""
    sub = AnswerSubmission(
        question_id="q-001",
        selected_option_id="B",
        time_taken_seconds=12.5,
    )
    assert sub.selected_option_id == "B"
    assert sub.time_taken_seconds == 12.5

    res = AnswerResult(
        is_correct=False,
        correct_option_id="A",
        explanation="1/4 + 2/4 = 3/4. Denominators stay the same.",
        misconception_tag="add_denominators",
        misconception_feedback="Remember to keep the common denominator when adding fractions!",
        xp_earned=5,
    )
    assert not res.is_correct
    assert res.misconception_tag == "add_denominators"
    assert res.xp_earned == 5


def test_fallback_bank_validates_against_question_schema() -> None:
    """Test that all items in data/fallback_bank.json strictly adhere to Question schema."""
    bank_path = Path(__file__).resolve().parent.parent / "data" / "fallback_bank.json"
    assert bank_path.exists(), "fallback_bank.json must exist"

    with open(bank_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    assert isinstance(items, list)
    assert len(items) > 0

    for item in items:
        q = Question.model_validate(item)
        assert q.grade in (5, 6)
        assert q.board == "georgia"  # Default board value
        assert q.correct_option_id in [opt.id for opt in q.options]


def test_question_and_template_board_field() -> None:
    """Test Question and QuestionTemplate support board field (default 'georgia', customizable to 'cbse')."""
    # Question with default board
    q_default = Question(
        id="q-geo-1",
        topic="fractions",
        grade=5,
        tier=Tier.EASY,
        stem="1/2 + 1/4 = ?",
        expression="1/2 + 1/4",
        options=[Option(id="A", text="3/4"), Option(id="B", text="2/6")],
        correct_option_id="A",
        explanation="Add fractions with common denominator.",
        standard_code="MGSE5.NF.1",
    )
    assert q_default.board == "georgia"

    # Question with CBSE board
    q_cbse = Question(
        id="q-cbse-1",
        board="cbse",
        topic="factors_multiples",
        grade=6,
        tier=Tier.MEDIUM,
        stem="Find the HCF of 12 and 18.",
        expression="gcd(12, 18)",
        options=[Option(id="A", text="6"), Option(id="B", text="36")],
        correct_option_id="A",
        explanation="The greatest common divisor of 12 and 18 is 6.",
        standard_code="CBSE6.MATH.01",
    )
    assert q_cbse.board == "cbse"
    assert q_cbse.standard_code == "CBSE6.MATH.01"

    # QuestionTemplate with CBSE board
    tmpl = QuestionTemplate(
        board="cbse",
        stem="Find the LCM of 4 and 6.",
        expression="lcm(4, 6)",
        standard_code="CBSE6.MATH.01",
        topic="factors_multiples",
        tier=Tier.EASY,
        question_type=QuestionType.LCM_GCD,
        claimed_answer="12",
    )
    assert tmpl.board == "cbse"
    assert tmpl.question_type == QuestionType.LCM_GCD


def test_curriculum_pack_schema_validation() -> None:
    """Test CurriculumPack, TopicConfig, and TierRule Pydantic models validate correctly."""
    tier_easy = TierRule(
        tier=Tier.EASY,
        description="Single-digit prime numbers and factor identification",
        operands_range={"min_val": 2, "max_val": 20},
        example_expression="factors(12)",
    )
    topic = TopicConfig(
        id="factors_multiples",
        title="Factors and Multiples",
        description="Prime numbers, HCF, LCM, and divisibility rules",
        standard_code="CBSE6.MATH.01",
        standard_title="Playing with Numbers",
        verified=True,
        tier_rules={"easy": tier_easy},
    )
    pack = CurriculumPack(
        board="cbse",
        board_name="Central Board of Secondary Education (NCERT Ganita Prakash)",
        grade=6,
        version="1.0.0",
        verified=True,
        topics=[topic],
    )

    assert pack.board == "cbse"
    assert pack.grade == 6
    assert len(pack.topics) == 1
    assert pack.get_topic("factors_multiples") is not None
    assert pack.get_topic("non_existent") is None
    assert pack.get_topic("factors_multiples").title == "Factors and Multiples"


def test_cbse_enums_supported() -> None:
    """Test MathTopic and QuestionType include CBSE Class 6 topics."""
    assert MathTopic.FACTORS_MULTIPLES.value == "factors_multiples"
    assert MathTopic.INTEGERS.value == "integers"
    assert QuestionType.FACTORS_MULTIPLES.value == "factors_multiples"
    assert QuestionType.LCM_GCD.value == "lcm_gcd"
    assert QuestionType.INTEGERS.value == "integers"

