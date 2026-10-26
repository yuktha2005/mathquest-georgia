"""Adaptive engine for MathQuest Georgia.

Core Responsibilities:
1. Dynamic Tier Adjustment:
   - Rule: 2 correct in a row moves up one tier; 1 wrong moves down one tier (clamped between easy and hard).
2. Per-Topic Mastery (0-100):
   - Elo-style expected probability vs actual outcome, weighted by difficulty tier.
3. Scoring & XP:
   - Base points (easy 10, medium 20, hard 30), minus 5 per hint, plus streak bonus.
4. Badge Progression:
   - First Steps, 5-Streak, Fraction Master, Comeback Kid, Perfect Round.
"""

from __future__ import annotations

import logging
from typing import Literal
from app.schemas import AnswerResult, AnswerSubmission, Option, Question, Tier
from app.services.question_builder import get_question_by_id

logger = logging.getLogger(__name__)

# Diagnostic Feedback Map for Curated Misconceptions
MISCONCEPTION_FEEDBACK_MAP: dict[str, str] = {
    # Fractions (Add/Sub)
    "added_denominators": "Remember to find a common denominator first! Never add or subtract denominators directly.",
    "no_common_denominator": "Before adding or subtracting fractions, make sure they have a common denominator.",
    "forgot_to_simplify": "Great work solving! Just remember to simplify your final fraction to lowest terms.",
    "sign_confusion": "Take a close look at the operation symbol (+ or −) before calculating.",
    "numerator_arithmetic_error": "Check your addition or subtraction in the numerator carefully.",
    # Fractions (Mul/Div)
    "multiplied_instead_of_inverting": "To divide fractions, multiply by the reciprocal (flip the second fraction)!",
    "flipped_wrong_fraction": "Keep the first fraction as-is and flip ONLY the second fraction (the divisor) when dividing.",
    "inverted_product": "Check the numerator and denominator placement of your final answer.",
    "forgot_to_simplify_mult": "Don't forget to simplify your product to lowest terms!",
    # Decimals
    "misaligned_decimal_point": "Always line up your decimal points vertically before adding or subtracting decimals!",
    "ignored_place_value": "Be careful with place value! Digits after the decimal point represent tenths and hundredths, not whole numbers.",
    "dropped_trailing_zero": "Remember to add placeholder zeros (like 4.0 or 0.50) when subtracting decimals to avoid place value confusion.",
    # Ratios
    "added_instead_of_scaled": "Ratios scale by multiplying or dividing, not by adding or subtracting the same number.",
    "inverted_ratio": "Watch the order of terms in your ratio! The first quantity must match the first number.",
    # Factors & Multiples (CBSE)
    "added_numbers": "Factors and multiples are found through multiplication and division, not addition!",
    "composite_not_prime": "Be careful! That number is composite because it has more than two factors. A prime number has only 1 and itself.",
    "composite_factor": "Remember that prime factors must only be divisible by 1 and themselves.",
    "other_prime_factor": "That is a prime factor, but check if there is a smaller one that fits the question!",
    "missed_one_factor": "Count all factors carefully by listing factor pairs from smallest to largest.",
    "counted_composite": "Make sure you only count prime factors, not composite ones.",
    "largest_factor": "Check whether the question asked for the smallest prime factor, the HCF, or the count of factors.",
    "common_factor_not_greatest": "That is a common factor, but check if there is a larger (highest) common factor!",
    "small_factor": "Look for larger common factors that divide both numbers evenly.",
    "hcf_instead_of_lcm": "LCM is the smallest multiple shared by both numbers, not the highest common factor (HCF)!",
    "lcm_confusion": "Make sure to find the HCF (highest factor that divides both), not the LCM!",
    "product_without_dividing_gcd": "To find the LCM, divide the product of the two numbers by their greatest common divisor (GCD).",
    "multiple_of_15_not_12": "Check that your multiple is divisible by BOTH numbers, not just one of them.",
    # Integers (CBSE)
    "wrong_sign_add": "When adding a positive to a negative, move right on the number line toward the positive numbers.",
    "ignored_negative": "Pay attention to the negative sign! Negative numbers decrease the total value.",
    "sign_flip": "Check the sign of the number with the larger absolute value to determine the result's sign.",
    "subtracted_magnitudes": "When subtracting a positive from a negative (like -7 - 4), you move further left into the negatives (-11).",
    "wrong_sign": "Remember: a negative minus a positive results in an even smaller negative number.",
    "sign_error": "Watch your signs! Adding a negative number is equivalent to subtracting.",
    "added_magnitudes": "Don't just add the numbers together; take their positive and negative signs into account.",
    "added_positives": "Remember that the negative sign changes the calculation from simple positive addition.",
    "treated_double_negative_as_minus": "Subtracting a negative number turns into addition! -(-x) is equal to +x.",
    "all_positive": "Take negative values into account rather than treating all numbers as positive.",
    "order_of_operations_confusion": "Work from left to right when evaluating addition and subtraction of integers.",
    "added_all_magnitudes": "Follow the positive and negative signs on each integer rather than adding all values together.",
    "added_before_multiply": "Remember order of operations (PEMDAS / BODMAS): multiply before adding or subtracting!",
    "wrong_operations": "Check whether each step involves multiplication or addition.",
    # Geometry
    "confused_area_perimeter": "Area measures the space inside (length × width), while perimeter measures the distance around the outside.",
    "forgot_to_halve_triangle": "Remember the triangle area formula: Area = (base × height) ÷ 2! Don't forget to divide by 2.",
    "double_counted": "Make sure you did not accidentally double your final measurement.",
    "halved_both_dimensions": "Only divide by 2 once when finding triangle area (base × height ÷ 2), not both dimensions.",
    "added_dimensions": "To find area, multiply the dimensions together; don't just add them!",
    "square_confused_perimeter_with_area": "For a square, Area is side × side (s²), while Perimeter is 4 × side.",
    "parallelogram_used_side_instead_of_height": "For a parallelogram, Area = base × perpendicular height, not the slant side length!",
}

DEFAULT_MISCONCEPTION_FEEDBACK = (
    "Take another look at the steps, double-check your calculations, and try again!"
)

# Ordered tier progression
TIER_ORDER: list[Tier] = [Tier.EASY, Tier.MEDIUM, Tier.HARD]


def _to_tier(tier: Tier | str) -> Tier:
    """Normalize input into a Tier enum."""
    if isinstance(tier, Tier):
        return tier
    val = str(tier).lower().strip()
    return Tier(val)


def next_tier(
    current_tier: Tier | str,
    history: list[bool],
    consecutive_correct: int | None = None,
) -> Tier:
    """Calculate the next difficulty tier based on recent answer performance.

    Rules:
    - 2 correct in a row: moves UP one tier (clamped at HARD).
    - 1 wrong: moves DOWN one tier (clamped at EASY).
    - Otherwise (e.g. 1 correct after wrong, or empty history): stays at current tier.
    """
    tier = _to_tier(current_tier)
    if not history:
        return tier

    # Rule: 1 wrong moves down one tier
    if history[-1] is False:
        if tier == Tier.HARD:
            return Tier.MEDIUM
        return Tier.EASY  # MEDIUM -> EASY, EASY -> EASY

    # Rule: 2 correct in a row at this tier moves up one tier
    if consecutive_correct is not None:
        if consecutive_correct >= 2:
            if tier == Tier.EASY:
                return Tier.MEDIUM
            return Tier.HARD
        return tier

    if len(history) >= 2 and history[-1] is True and history[-2] is True:
        if tier == Tier.EASY:
            return Tier.MEDIUM
        return Tier.HARD  # MEDIUM -> HARD, HARD -> HARD

    # 1 correct so far or alternating: stay at current tier
    return tier


def update_mastery(
    current_mastery: float,
    correct: bool,
    tier: Tier | str,
    k_factor: float = 10.0,
) -> float:
    """Update topic mastery (0-100) using an Elo-style rating formula weighted by tier.

    Elo Mechanics:
    - Benchmark difficulty R_q: Easy (30), Medium (50), Hard (70).
    - Expected score E = 1 / (1 + 10^((R_q - M) / 40)).
    - Change Delta M = K * (Actual - E).
    - Output is strictly clamped between 0.0 and 100.0.
    """
    tier_obj = _to_tier(tier)
    mastery = max(0.0, min(100.0, float(current_mastery)))

    # Benchmark rating per tier
    tier_ratings = {
        Tier.EASY: 30.0,
        Tier.MEDIUM: 50.0,
        Tier.HARD: 70.0,
    }

    r_q = tier_ratings[tier_obj]

    # Logistic expected probability of success
    exponent = (r_q - mastery) / 40.0
    exponent = max(-10.0, min(10.0, exponent))
    expected = 1.0 / (1.0 + (10.0 ** exponent))

    actual = 1.0 if correct else 0.0
    delta = k_factor * (actual - expected)

    new_mastery = round(mastery + delta, 1)
    return max(0.0, min(100.0, new_mastery))



def score_answer(
    correct: bool,
    tier: Tier | str,
    hints_used: int = 0,
    streak: int = 0,
) -> int:
    """Calculate points earned for answering a question.

    Rules:
    - Easy: 10 base points
    - Medium: 20 base points
    - Hard: 30 base points
    - Minus 5 points per hint used
    - Plus a streak bonus for consecutive correct answers (streak >= 2)
    - If answer is incorrect: 0 points.
    - If answer is correct: minimum 1 point guaranteed.
    """
    if not correct:
        return 0

    tier_obj = _to_tier(tier)
    base_table = {
        Tier.EASY: 10,
        Tier.MEDIUM: 20,
        Tier.HARD: 30,
    }
    base = base_table[tier_obj]

    # Deduct 5 per hint used
    hint_penalty = max(0, hints_used) * 5
    base_after_hints = max(0, base - hint_penalty)

    # Streak bonus: +2 points per streak above 1, capped at 20 bonus points
    streak_bonus = min(max(0, streak - 1) * 2, 20) if streak > 1 else 0

    total_points = base_after_hints + streak_bonus
    # Rewarding correct answers with at least 1 point
    return max(1, total_points)


def badges(session_stats: dict) -> list[str]:
    """Evaluate earned badges from cumulative or session statistics.

    Supported Badges:
    - First Steps: Answered at least 1 question.
    - 5-Streak: Achieved a consecutive streak of 5 or more.
    - Fraction Master: Fraction mastery >= 80 or answered 5+ fraction problems correctly.
    - Comeback Kid: Got a question correct immediately after answering one wrong.
    - Perfect Round: Completed a round of 5+ questions with 100% accuracy.
    """
    unlocked: list[str] = []

    # 1. First Steps
    total_answered = (
        session_stats.get("total_answered", 0)
        or session_stats.get("questions_answered", 0)
        or session_stats.get("correct_count", 0)
    )
    if total_answered >= 1:
        unlocked.append("First Steps")

    # 2. 5-Streak
    current_streak = session_stats.get("streak", 0)
    best_streak = session_stats.get("best_streak", 0)
    if current_streak >= 5 or best_streak >= 5:
        unlocked.append("5-Streak")

    # 3. Fraction Master
    fraction_mastery = session_stats.get("fraction_mastery", 0)
    topic_mastery = session_stats.get("topic_mastery", {})
    if isinstance(topic_mastery, dict):
        fraction_mastery = max(fraction_mastery, topic_mastery.get("fractions", 0))
    fractions_correct = session_stats.get("fractions_correct", 0)

    if fraction_mastery >= 80 or fractions_correct >= 5:
        unlocked.append("Fraction Master")

    # 4. Decimal Dynamo
    decimal_mastery = session_stats.get("decimal_mastery", 0)
    if isinstance(topic_mastery, dict):
        decimal_mastery = max(decimal_mastery, topic_mastery.get("decimals", 0))
    decimals_correct = session_stats.get("decimals_correct", 0)
    if decimal_mastery >= 80 or decimals_correct >= 5:
        unlocked.append("Decimal Dynamo")

    # 5. Ratio Ranger
    ratio_mastery = session_stats.get("ratio_mastery", 0)
    if isinstance(topic_mastery, dict):
        ratio_mastery = max(ratio_mastery, topic_mastery.get("ratios", 0))
    ratios_correct = session_stats.get("ratios_correct", 0)
    if ratio_mastery >= 80 or ratios_correct >= 5:
        unlocked.append("Ratio Ranger")

    # 6. Geometry Giant
    geometry_mastery = session_stats.get("geometry_mastery", 0)
    if isinstance(topic_mastery, dict):
        geometry_mastery = max(geometry_mastery, topic_mastery.get("geometry", 0))
    geometry_correct = session_stats.get("geometry_correct", 0)
    if geometry_mastery >= 80 or geometry_correct >= 5:
        unlocked.append("Geometry Giant")

    # 7. CBSE Champion
    cbse_mastery = session_stats.get("cbse_mastery", 0)
    if isinstance(topic_mastery, dict):
        cbse_mastery = max(
            cbse_mastery,
            topic_mastery.get("factors_multiples", 0),
            topic_mastery.get("integers", 0),
        )
    cbse_correct = session_stats.get("cbse_correct", 0)
    if cbse_mastery >= 80 or cbse_correct >= 5:
        unlocked.append("CBSE Champion")

    # 8. Tenacious Thinker (solved a HARD question)
    if session_stats.get("solved_hard", False) is True:
        unlocked.append("Tenacious Thinker")

    # 9. Comeback Kid
    if session_stats.get("comeback", False) is True:
        unlocked.append("Comeback Kid")

    # 10. Perfect Round
    round_total = session_stats.get("round_total", 0)
    round_correct = session_stats.get("round_correct", 0)
    round_wrong = session_stats.get("round_wrong", 0)
    round_completed = session_stats.get("round_completed", False)

    if session_stats.get("perfect_round", False) is True:
        unlocked.append("Perfect Round")
    elif round_completed and round_total >= 5 and round_wrong == 0 and round_correct == round_total:
        unlocked.append("Perfect Round")

    return unlocked


def get_new_badges(session_stats: dict, already_earned: list[str]) -> list[str]:
    """Return only the badges that were earned in this turn and not previously awarded."""
    all_earned = badges(session_stats)
    return [b for b in all_earned if b not in already_earned]


def evaluate_submission(submission: AnswerSubmission) -> AnswerResult:
    """Evaluate an answer submission and compute all adaptive and gamified progressions."""
    # 1. Attempt question resolution via memory cache or fallback bank
    question = get_question_by_id(submission.question_id)

    # Resolve options and correct option
    correct_option_id = submission.correct_option_id
    options: list[Option] = submission.options or []
    explanation = submission.explanation or "Great practice! Review the steps to strengthen your understanding."
    topic = submission.topic or "general"
    tier = submission.tier

    if question:
        correct_option_id = question.correct_option_id
        options = question.options
        explanation = question.explanation
        topic = question.topic
        tier = question.tier

    if not correct_option_id:
        # Default fallback if question metadata was not passed and not cached
        correct_option_id = "A"

    # Find correct answer text
    correct_answer_text = ""
    for opt in options:
        if opt.id == correct_option_id:
            correct_answer_text = opt.text
            break

    # 2. Check correctness
    is_correct = (submission.selected_option_id.strip().upper() == correct_option_id.strip().upper())

    # 3. Misconception lookup
    misconception_tag: str | None = None
    misconception_feedback: str | None = None

    if not is_correct:
        # Locate chosen distractor
        selected_opt: Option | None = None
        for opt in options:
            if opt.id.strip().upper() == submission.selected_option_id.strip().upper():
                selected_opt = opt
                break

        if selected_opt and selected_opt.misconception_tag:
            misconception_tag = selected_opt.misconception_tag
            misconception_feedback = MISCONCEPTION_FEEDBACK_MAP.get(
                misconception_tag, DEFAULT_MISCONCEPTION_FEEDBACK
            )
        else:
            misconception_feedback = DEFAULT_MISCONCEPTION_FEEDBACK

    # 4. Adaptive State Updates
    updated_history = list(submission.history) + [is_correct]
    new_streak = (submission.streak + 1) if is_correct else 0
    points = score_answer(
        correct=is_correct,
        tier=tier,
        hints_used=submission.hints_used,
        streak=new_streak,
    )

    # 5. Session Stats & Tier Transition Tracking
    stats = dict(submission.session_stats)
    if "consecutive_at_tier" in stats:
        consec_at_tier = stats["consecutive_at_tier"]
    else:
        consec_at_tier = submission.streak

    if is_correct:
        consec_at_tier += 1
    else:
        consec_at_tier = 0

    adapted_tier = next_tier(
        current_tier=tier,
        history=updated_history,
        consecutive_correct=consec_at_tier,
    )

    if adapted_tier != tier:
        # Reset consecutive counter on tier transition (up or down)
        stats["consecutive_at_tier"] = 0
    else:
        stats["consecutive_at_tier"] = consec_at_tier

    new_mastery = update_mastery(
        current_mastery=submission.current_mastery,
        correct=is_correct,
        tier=tier,
    )
    stats["total_answered"] = stats.get("total_answered", 0) + 1
    if is_correct:
        stats["correct_count"] = stats.get("correct_count", 0) + 1
    stats["streak"] = new_streak
    stats["best_streak"] = max(stats.get("best_streak", 0), new_streak)

    # Comeback Kid detection: if previous answer in history was wrong and this one is correct
    if len(submission.history) >= 1 and submission.history[-1] is False and is_correct:
        stats["comeback"] = True

    # Topic, tier, and board tracking for badges
    topic_str = topic.lower()
    board_str = (getattr(submission, "board", None) or (question.board if question else "georgia")).lower()

    if is_correct and tier == Tier.HARD:
        stats["solved_hard"] = True

    if topic_str == "fractions":
        stats["fraction_mastery"] = new_mastery
        if is_correct:
            stats["fractions_correct"] = stats.get("fractions_correct", 0) + 1
    elif topic_str == "decimals":
        stats["decimal_mastery"] = new_mastery
        if is_correct:
            stats["decimals_correct"] = stats.get("decimals_correct", 0) + 1
    elif topic_str == "ratios":
        stats["ratio_mastery"] = new_mastery
        if is_correct:
            stats["ratios_correct"] = stats.get("ratios_correct", 0) + 1
    elif topic_str == "geometry":
        stats["geometry_mastery"] = new_mastery
        if is_correct:
            stats["geometry_correct"] = stats.get("geometry_correct", 0) + 1

    if board_str == "cbse" or topic_str in ("factors_multiples", "integers"):
        stats["cbse_mastery"] = max(stats.get("cbse_mastery", 0.0), new_mastery)
        if is_correct:
            stats["cbse_correct"] = stats.get("cbse_correct", 0) + 1

    already_earned = list(stats.get("earned_badges", []))
    newly_earned = get_new_badges(stats, already_earned)
    stats["earned_badges"] = already_earned + [b for b in newly_earned if b not in already_earned]

    return AnswerResult(
        is_correct=is_correct,
        correct_option_id=correct_option_id,
        correct_answer=correct_answer_text,
        explanation=explanation,
        misconception_tag=misconception_tag,
        misconception_feedback=misconception_feedback,
        points=points,
        xp_earned=points,
        next_tier=adapted_tier,
        new_mastery=new_mastery,
        new_badges=newly_earned,
        streak=new_streak,
        board=board_str,
    )
