"""Unit and integration tests for question builder pipeline with mocked LLM."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import (
    BatchQuestionResponse,
    Question,
    QuestionTemplate,
    QuestionType,
    Tier,
)
from app.services.infographic import get_topic_infographic
from app.services.question_builder import (
    build_question_pipeline,
    build_questions_batch,
    get_fallback_question,
)
from app.services.rag import retrieve_standards
from app.services.verify import evaluate

client = TestClient(app)


def test_question_builder_happy_path() -> None:
    """Test successful question generation on first attempt with mocked LLM."""
    mock_template = QuestionTemplate(
        stem="Leo mixes 3/4 cup of sugar with 1/2 cup of flour. How many cups total?",
        expression="3/4 + 1/2",
        standard_code="MGSE5.NF.1",
        topic="fractions",
        tier=Tier.MEDIUM,
        question_type=QuestionType.FRACTION_ADD_SUB,
        operands=["3/4", "1/2"],
        claimed_answer="5/4",
    )
    mock_llm = MagicMock(return_value=mock_template)

    question, retries, latency_ms, used_fallback = build_question_pipeline(
        grade=5,
        topic="fractions",
        tier=Tier.MEDIUM,
        llm_func=mock_llm,
    )

    assert not used_fallback
    assert retries == 0
    assert latency_ms > 0
    assert question.topic == "fractions"
    assert question.grade == 5
    assert question.tier == Tier.MEDIUM
    assert len(question.options) == 4
    assert question.correct_option_id in ["A", "B", "C", "D"]

    # Verify true answer 5/4 or 1 1/4 is in options
    correct_opt = next(opt for opt in question.options if opt.id == question.correct_option_id)
    assert correct_opt.text in ("5/4", "1 1/4")
    assert correct_opt.misconception_tag is None

    # Verify distractors have misconception tags
    distractors = [opt for opt in question.options if opt.id != question.correct_option_id]
    assert len(distractors) == 3
    for dist in distractors:
        assert dist.misconception_tag is not None


def test_question_builder_claimed_answer_mismatch_triggers_retry() -> None:
    """Test that claimed_answer != evaluate(expression) triggers repair retry."""
    # Attempt 0: Expression is 1/4 + 2/4 (3/4), but claimed_answer is hallucinated 5/4
    bad_template = QuestionTemplate(
        stem="Maya painted 1/4 of a fence and then 2/4 of it. How much did she paint?",
        expression="1/4 + 2/4",
        standard_code="MGSE5.NF.1",
        topic="fractions",
        tier=Tier.EASY,
        question_type=QuestionType.FRACTION_ADD_SUB,
        operands=["1/4", "2/4"],
        claimed_answer="5/4",  # Mismatch! 1/4 + 2/4 != 5/4
    )
    # Attempt 1: Repaired template with matching claimed_answer
    good_template = QuestionTemplate(
        stem="Maya painted 1/4 of a fence and then 2/4 of it. How much did she paint?",
        expression="1/4 + 2/4",
        standard_code="MGSE5.NF.1",
        topic="fractions",
        tier=Tier.EASY,
        question_type=QuestionType.FRACTION_ADD_SUB,
        operands=["1/4", "2/4"],
        claimed_answer="3/4",  # Correct!
    )

    mock_llm = MagicMock(side_effect=[bad_template, good_template])

    question, retries, latency_ms, used_fallback = build_question_pipeline(
        grade=5,
        topic="fractions",
        tier=Tier.EASY,
        llm_func=mock_llm,
    )

    assert not used_fallback
    assert retries == 1  # Successfully repaired on retry 1
    assert mock_llm.call_count == 2
    assert question.grade == 5


def test_question_builder_repair_retry_success() -> None:
    """Test that pipeline recovers on attempt 2 after first attempt fails with invalid math."""
    mock_bad_template = QuestionTemplate(
        stem="Bad math problem",
        expression="5 / 0",  # Triggers DivisionByZeroError in verify.py
        standard_code="MGSE5.NF.1",
        topic="fractions",
        tier=Tier.EASY,
        question_type=QuestionType.FRACTION_ADD_SUB,
        operands=["5", "0"],
        claimed_answer="0",
    )
    mock_good_template = QuestionTemplate(
        stem="Maya painted 1/4 of a fence and then 2/4 of it. How much did she paint?",
        expression="1/4 + 2/4",
        standard_code="MGSE5.NF.1",
        topic="fractions",
        tier=Tier.EASY,
        question_type=QuestionType.FRACTION_ADD_SUB,
        operands=["1/4", "2/4"],
        claimed_answer="3/4",
    )

    mock_llm = MagicMock(side_effect=[mock_bad_template, mock_good_template])

    question, retries, latency_ms, used_fallback = build_question_pipeline(
        grade=5,
        topic="fractions",
        tier=Tier.EASY,
        llm_func=mock_llm,
    )

    assert not used_fallback
    assert retries == 1
    assert mock_llm.call_count == 2


def test_question_builder_fallback_after_max_retries() -> None:
    """Test fallback bank is returned when all repair retries are exhausted."""
    mock_llm = MagicMock(side_effect=ValueError("Persistent schema validation error"))

    question, retries, latency_ms, used_fallback = build_question_pipeline(
        grade=6,
        topic="geometry",
        tier=Tier.HARD,
        llm_func=mock_llm,
    )

    assert used_fallback is True
    assert retries == 2  # Max 2 repair retries attempted
    assert mock_llm.call_count == 3  # Initial attempt + 2 retries
    assert question.topic == "geometry"
    assert question.tier == Tier.HARD
    assert len(question.options) == 4


def test_every_fallback_entry_matches_evaluate() -> None:
    """Test all 48 fallback entries strictly evaluate to their correct option's text."""
    fallback_path = Path(__file__).resolve().parent.parent / "data" / "fallback_bank.json"
    with open(fallback_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    assert len(items) == 48, f"Expected exactly 48 fallback questions, got {len(items)}"

    # Check distribution across Grade 5 and 6, 4 topics, and 3 tiers
    grades = {item["grade"] for item in items}
    topics = {item["topic"] for item in items}
    tiers = {item["tier"] for item in items}

    assert grades == {5, 6}
    assert topics == {"fractions", "decimals", "ratios", "geometry"}
    assert tiers == {"easy", "medium", "hard"}

    for item in items:
        # Validate Pydantic schema
        q = Question.model_validate(item)

        # Ground truth evaluation of expression
        true_val = evaluate(q.expression)

        # Evaluation of correct option's text
        correct_opt = next(opt for opt in q.options if opt.id == q.correct_option_id)
        claimed_val = evaluate(correct_opt.text)

        assert true_val == claimed_val, (
            f"Question ID {q.id} expression '{q.expression}' ({true_val}) "
            f"does not match correct option '{correct_opt.text}' ({claimed_val})"
        )


def test_post_api_question_batch_of_10() -> None:
    """Test POST /api/question supporting a batch of 10 for a full round."""
    mock_template = QuestionTemplate(
        stem="Elena ran 2.5 miles on Monday and 1.75 miles on Tuesday. How far did she run?",
        expression="2.5 + 1.75",
        standard_code="MGSE5.NBT.7",
        topic="decimals",
        tier=Tier.MEDIUM,
        question_type=QuestionType.DECIMAL_OPS,
        operands=["2.5", "1.75"],
        claimed_answer="4.25",
    )

    with patch("app.services.question_builder.generate_question_template", return_value=mock_template):
        response = client.post(
            "/api/question",
            json={"grade": 5, "topic": "decimals", "tier": "medium", "count": 10},
        )

    assert response.status_code == 200
    data = response.json()
    batch = BatchQuestionResponse.model_validate(data)
    assert batch.count == 10
    assert len(batch.questions) == 10
    for q in batch.questions:
        assert q.topic == "decimals"
        assert len(q.options) == 4


def test_rag_local_standards_fallback() -> None:
    """Test RAG retrieves standards from local markdown files when Supabase is unconfigured."""
    # With no SUPABASE_URL, retrieve_standards must read data/standards/*.md
    results = retrieve_standards(query="unlike denominators fractions", topic="fractions", grade=5)
    assert len(results) > 0
    assert any("MGSE5.NF" in r["standard_code"] for r in results)
    assert results[0]["source"] == "local_standards_fallback"


def test_infographic_cached_preference() -> None:
    """Test /api/infographic prefers pre-generated cached files."""
    info = get_topic_infographic("fractions", refresh=False)
    assert info["source"] == "cache"
    assert info["format"] == "svg"

    response = client.get("/api/infographic?topic=fractions")
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "fractions"
    assert "svg" in data["format"]


def test_evaluation_api_reads_results_file() -> None:
    """Test /api/eval reads results from backend/eval/results.json with configurable N defaulting to 3."""
    response = client.get("/api/eval")
    assert response.status_code == 200
    data = response.json()
    assert data["eval_n"] == 3
    assert "pass_rate_percentage" in data
    assert "avg_latency_ms" in data
    assert len(data["samples"]) >= 1
