"""Comprehensive unit and integration tests for the MathQuest Georgia adaptive engine."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import AnswerResult, AnswerSubmission, Option, Question, Tier
from app.services.adaptive import (
    MISCONCEPTION_FEEDBACK_MAP,
    badges,
    get_new_badges,
    next_tier,
    score_answer,
    update_mastery,
)
from app.services.question_builder import get_question_by_id, register_question

client = TestClient(app)


# ==========================================
# 1. Tests for next_tier()
# ==========================================

def test_next_tier_empty_history_preserves_tier() -> None:
    """Empty history should maintain the current difficulty tier."""
    assert next_tier(Tier.EASY, []) == Tier.EASY
    assert next_tier(Tier.MEDIUM, []) == Tier.MEDIUM
    assert next_tier(Tier.HARD, []) == Tier.HARD


def test_next_tier_two_correct_moves_up_one_tier() -> None:
    """Two correct answers in a row must advance difficulty by exactly one tier."""
    # EASY -> MEDIUM
    assert next_tier(Tier.EASY, [True, True]) == Tier.MEDIUM
    assert next_tier("easy", [False, True, True]) == Tier.MEDIUM

    # MEDIUM -> HARD
    assert next_tier(Tier.MEDIUM, [True, True]) == Tier.HARD
    assert next_tier("medium", [True, False, True, True]) == Tier.HARD

    # HARD -> HARD (clamped at ceiling)
    assert next_tier(Tier.HARD, [True, True]) == Tier.HARD
    assert next_tier("hard", [True, True, True]) == Tier.HARD


def test_next_tier_one_wrong_moves_down_one_tier() -> None:
    """A single wrong answer must drop difficulty by one tier, clamped at EASY."""
    # HARD -> MEDIUM
    assert next_tier(Tier.HARD, [False]) == Tier.MEDIUM
    assert next_tier("hard", [True, True, False]) == Tier.MEDIUM

    # MEDIUM -> EASY
    assert next_tier(Tier.MEDIUM, [False]) == Tier.EASY
    assert next_tier("medium", [True, False]) == Tier.EASY

    # EASY -> EASY (clamped at floor)
    assert next_tier(Tier.EASY, [False]) == Tier.EASY
    assert next_tier("easy", [False, False]) == Tier.EASY


def test_next_tier_single_correct_does_not_advance() -> None:
    """A single correct answer should not advance the tier until 2 in a row are reached."""
    assert next_tier(Tier.EASY, [True]) == Tier.EASY
    assert next_tier(Tier.MEDIUM, [True]) == Tier.MEDIUM
    assert next_tier(Tier.EASY, [False, True]) == Tier.EASY
    assert next_tier(Tier.MEDIUM, [False, True]) == Tier.MEDIUM


# ==========================================
# 2. Tests for update_mastery()
# ==========================================

def test_update_mastery_correct_increases_score() -> None:
    """Correct answers should increase topic mastery."""
    initial = 50.0
    new_mastery = update_mastery(initial, correct=True, tier=Tier.MEDIUM)
    assert new_mastery > initial
    assert isinstance(new_mastery, float)


def test_update_mastery_wrong_decreases_score() -> None:
    """Incorrect answers should decrease topic mastery."""
    initial = 50.0
    new_mastery = update_mastery(initial, correct=False, tier=Tier.MEDIUM)
    assert new_mastery < initial
    assert isinstance(new_mastery, float)


def test_update_mastery_hard_tier_rewards_more_than_easy() -> None:
    """Solving a HARD question should yield a larger mastery gain than solving an EASY question."""
    initial = 50.0
    gain_easy = update_mastery(initial, correct=True, tier=Tier.EASY) - initial
    gain_hard = update_mastery(initial, correct=True, tier=Tier.HARD) - initial
    assert gain_hard > gain_easy


def test_update_mastery_failing_easy_penalizes_more_than_failing_hard() -> None:
    """Failing an EASY question when mastery is high indicates a larger gap than failing HARD."""
    high_mastery = 80.0
    drop_easy = high_mastery - update_mastery(high_mastery, correct=False, tier=Tier.EASY)
    drop_hard = high_mastery - update_mastery(high_mastery, correct=False, tier=Tier.HARD)
    assert drop_easy > drop_hard


def test_update_mastery_clamped_bounds() -> None:
    """Mastery score must strictly stay within 0.0 and 100.0."""
    # Ceiled at 100.0
    assert update_mastery(99.0, correct=True, tier=Tier.HARD) <= 100.0
    assert update_mastery(100.0, correct=True, tier=Tier.HARD) == 100.0

    # Floored at 0.0
    assert update_mastery(1.0, correct=False, tier=Tier.EASY) >= 0.0
    assert update_mastery(0.0, correct=False, tier=Tier.EASY) == 0.0


# ==========================================
# 3. Tests for score_answer()
# ==========================================

def test_score_answer_wrong_yields_zero_points() -> None:
    """Incorrect answers always award 0 points."""
    assert score_answer(correct=False, tier=Tier.EASY) == 0
    assert score_answer(correct=False, tier=Tier.MEDIUM, streak=5) == 0
    assert score_answer(correct=False, tier=Tier.HARD, hints_used=1) == 0


def test_score_answer_base_points_by_tier() -> None:
    """Base points: Easy 10, Medium 20, Hard 30 (with no hints and no streak)."""
    assert score_answer(correct=True, tier=Tier.EASY) == 10
    assert score_answer(correct=True, tier=Tier.MEDIUM) == 20
    assert score_answer(correct=True, tier=Tier.HARD) == 30


def test_score_answer_hint_deductions() -> None:
    """Each hint used deducts 5 points from base score."""
    # Medium (20) with 1 hint -> 15
    assert score_answer(correct=True, tier=Tier.MEDIUM, hints_used=1) == 15
    # Medium (20) with 2 hints -> 10
    assert score_answer(correct=True, tier=Tier.MEDIUM, hints_used=2) == 10
    # Hard (30) with 3 hints -> 15
    assert score_answer(correct=True, tier=Tier.HARD, hints_used=3) == 15


def test_score_answer_guaranteed_minimum_point_for_correct() -> None:
    """Even if hint penalties exceed base points, a correct answer yields at least 1 point."""
    # Easy (10) with 3 hints (-15) -> clamped floor of 1 point
    assert score_answer(correct=True, tier=Tier.EASY, hints_used=3) >= 1


def test_score_answer_streak_bonus() -> None:
    """Consecutive streaks of 2 or more award bonus points."""
    base_medium = score_answer(correct=True, tier=Tier.MEDIUM, streak=1)
    streak_2 = score_answer(correct=True, tier=Tier.MEDIUM, streak=2)
    streak_5 = score_answer(correct=True, tier=Tier.MEDIUM, streak=5)

    assert streak_2 > base_medium
    assert streak_5 > streak_2


# ==========================================
# 4. Tests for badges()
# ==========================================

def test_badges_first_steps() -> None:
    """First Steps badge awarded upon answering the first question."""
    assert "First Steps" in badges({"total_answered": 1})
    assert "First Steps" not in badges({"total_answered": 0})


def test_badges_5_streak() -> None:
    """5-Streak badge awarded when streak reaches 5."""
    assert "5-Streak" in badges({"streak": 5})
    assert "5-Streak" in badges({"best_streak": 6, "streak": 1})
    assert "5-Streak" not in badges({"streak": 4, "best_streak": 4})


def test_badges_fraction_master() -> None:
    """Fraction Master badge awarded at 80+ fraction mastery or 5+ fraction correct answers."""
    assert "Fraction Master" in badges({"fraction_mastery": 85})
    assert "Fraction Master" in badges({"topic_mastery": {"fractions": 82}})
    assert "Fraction Master" in badges({"fractions_correct": 5})
    assert "Fraction Master" not in badges({"fraction_mastery": 60, "fractions_correct": 3})


def test_badges_comeback_kid() -> None:
    """Comeback Kid badge awarded when bouncing back from a mistake."""
    assert "Comeback Kid" in badges({"comeback": True})
    assert "Comeback Kid" not in badges({"comeback": False})


def test_badges_perfect_round() -> None:
    """Perfect Round badge awarded when finishing 5+ questions with 100% accuracy."""
    assert "Perfect Round" in badges({"perfect_round": True})
    assert "Perfect Round" in badges({
        "round_completed": True,
        "round_total": 5,
        "round_correct": 5,
        "round_wrong": 0,
    })
    assert "Perfect Round" not in badges({
        "round_completed": True,
        "round_total": 5,
        "round_correct": 4,
        "round_wrong": 1,
    })


def test_get_new_badges_filters_existing() -> None:
    """get_new_badges() should only return badges not already in the user's collection."""
    stats = {"total_answered": 1, "streak": 5}
    already_earned = ["First Steps"]
    new_badges = get_new_badges(stats, already_earned)

    assert "5-Streak" in new_badges
    assert "First Steps" not in new_badges


# ==========================================
# 5. Integration Tests: POST /api/answer
# ==========================================

def test_api_answer_correct_submission() -> None:
    """Submit a correct answer and verify full adaptive response."""
    # Register a known test question
    test_q = Question(
        id="test-adaptive-q1",
        topic="fractions",
        grade=5,
        tier=Tier.EASY,
        stem="What is 1/4 + 2/4?",
        expression="1/4 + 2/4",
        options=[
            Option(id="A", text="3/4"),
            Option(id="B", text="3/8", misconception_tag="added_denominators"),
            Option(id="C", text="1/4", misconception_tag="no_common_denominator"),
            Option(id="D", text="6/8", misconception_tag="forgot_to_simplify"),
        ],
        correct_option_id="A",
        explanation="Add numerators over common denominator 4 to get 3/4.",
        standard_code="MGSE5.NF.1",
    )
    register_question(test_q)

    payload = {
        "question_id": "test-adaptive-q1",
        "selected_option_id": "A",
        "current_mastery": 50.0,
        "history": [True],
        "hints_used": 0,
        "streak": 1,
        "session_stats": {"total_answered": 1},
    }

    response = client.post("/api/answer", json=payload)
    assert response.status_code == 200

    data = response.json()
    result = AnswerResult.model_validate(data)

    assert result.is_correct is True
    assert result.correct_option_id == "A"
    assert result.correct_answer == "3/4"
    assert "3/4" in result.explanation
    assert result.misconception_tag is None
    assert result.misconception_feedback is None
    assert result.points > 0
    assert result.streak == 2
    # 2 correct in a row: EASY -> MEDIUM
    assert result.next_tier == Tier.MEDIUM
    assert result.new_mastery > 50.0


def test_api_answer_incorrect_with_misconception_tag() -> None:
    """Submit an incorrect answer and verify diagnostic misconception feedback."""
    test_q = Question(
        id="test-adaptive-q2",
        topic="decimals",
        grade=5,
        tier=Tier.MEDIUM,
        stem="What is 4.5 + 0.35?",
        expression="4.5 + 0.35",
        options=[
            Option(id="A", text="4.85"),
            Option(id="B", text="4.30", misconception_tag="misaligned_decimal_point"),
            Option(id="C", text="4.8", misconception_tag="dropped_trailing_zero"),
            Option(id="D", text="0.80", misconception_tag="ignored_place_value"),
        ],
        correct_option_id="A",
        explanation="Line up decimal places: 4.50 + 0.35 = 4.85.",
        standard_code="MGSE5.NBT.7",
    )
    register_question(test_q)

    payload = {
        "question_id": "test-adaptive-q2",
        "selected_option_id": "B",
        "current_mastery": 60.0,
        "history": [True, True],
        "hints_used": 1,
        "streak": 2,
    }

    response = client.post("/api/answer", json=payload)
    assert response.status_code == 200

    data = response.json()
    result = AnswerResult.model_validate(data)

    assert result.is_correct is False
    assert result.correct_option_id == "A"
    assert result.correct_answer == "4.85"
    assert result.misconception_tag == "misaligned_decimal_point"
    assert result.misconception_feedback == MISCONCEPTION_FEEDBACK_MAP["misaligned_decimal_point"]
    assert result.points == 0
    assert result.streak == 0
    # 1 wrong moves MEDIUM -> EASY
    assert result.next_tier == Tier.EASY
    assert result.new_mastery < 60.0


def test_api_answer_stateless_custom_payload() -> None:
    """Verify endpoint works statelessly when the frontend supplies question options."""
    payload = {
        "question_id": "client-gen-999",
        "selected_option_id": "C",
        "correct_option_id": "C",
        "topic": "geometry",
        "tier": "hard",
        "explanation": "Length 6 × Width 4 = Area 24.",
        "options": [
            {"id": "A", "text": "20", "misconception_tag": "confused_area_perimeter"},
            {"id": "B", "text": "12", "misconception_tag": "forgot_to_halve_triangle"},
            {"id": "C", "text": "24", "misconception_tag": None},
            {"id": "D", "text": "48", "misconception_tag": "double_counted"},
        ],
        "current_mastery": 70.0,
        "history": [False],
        "streak": 0,
        "session_stats": {"total_answered": 2, "earned_badges": ["First Steps"]},
    }

    response = client.post("/api/answer", json=payload)
    assert response.status_code == 200

    data = response.json()
    result = AnswerResult.model_validate(data)

    assert result.is_correct is True
    assert result.correct_option_id == "C"
    assert result.correct_answer == "24"
    assert result.points == 30  # Hard base points
    # Recovered from previous False: Comeback Kid awarded
    assert "Comeback Kid" in result.new_badges


def test_api_answer_fallback_question_lookup() -> None:
    """Verify that fallback bank IDs can be answered without manual pre-registration."""
    # fallback-g5-fractions-easy-1 is in data/fallback_bank.json
    fallback_q = get_question_by_id("fallback-g5-fractions-easy-1")
    assert fallback_q is not None


    payload = {
        "question_id": fallback_q.id,
        "selected_option_id": fallback_q.correct_option_id,
        "current_mastery": 45.0,
    }

    response = client.post("/api/answer", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["is_correct"] is True
    assert data["points"] > 0
    assert data["correct_option_id"] == fallback_q.correct_option_id
