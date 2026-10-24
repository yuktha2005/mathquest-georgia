"""Unit tests for the curated misconception distractor generator."""

from decimal import Decimal
from fractions import Fraction
import pytest

from app.services.misconceptions import (
    MisconceptionDistractor,
    get_decimal_distractors,
    get_factors_multiples_distractors,
    get_fraction_add_sub_distractors,
    get_fraction_mult_div_distractors,
    get_geometry_distractors,
    get_lcm_gcd_distractors,
    get_parallelogram_distractors,
    get_ratio_distractors,
)
from app.services.verify import format_answer


# ============================================================================
# Helpers
# ============================================================================

def assert_distractor_invariants(
    distractors: list[MisconceptionDistractor],
    correct_answer_str: str,
) -> None:
    """Validate all core invariants: exactly 3, unique, never equal to correct answer, non-empty."""
    assert len(distractors) == 3, f"Expected exactly 3 distractors, got {len(distractors)}"

    texts = [d.text.strip() for d in distractors]
    unique_texts = set(texts)

    assert len(unique_texts) == 3, f"Distractors must be unique: {texts}"
    assert correct_answer_str.strip() not in unique_texts, (
        f"Distractor cannot equal correct answer '{correct_answer_str}': {texts}"
    )

    for d in distractors:
        assert d.text.strip(), "Distractor text must not be empty"
        assert d.misconception_tag.strip(), "Misconception tag must not be empty"
        assert d.feedback.strip(), "Feedback sentence must not be empty"


# ============================================================================
# 1. Fractions: Addition & Subtraction Tests
# ============================================================================

def test_fractions_addition_misconceptions() -> None:
    """Test fraction addition includes added_denominators, no_common_denominator, forgot_to_simplify."""
    f1 = Fraction(1, 4)
    f2 = Fraction(2, 4)
    correct_str = format_answer(f1 + f2, style="fraction")  # "3/4"

    distractors = get_fraction_add_sub_distractors(f1, f2, "+", raw_operands=(1, 4, 2, 4))
    assert_distractor_invariants(distractors, correct_str)

    tags = {d.misconception_tag for d in distractors}
    assert "added_denominators" in tags
    assert "forgot_to_simplify" in tags

    # Verify added_denominators value: (1 + 2)/(4 + 4) = 3/8
    added_denom_d = next(d for d in distractors if d.misconception_tag == "added_denominators")
    assert added_denom_d.text == "3/8"
    assert "Never add denominators together" in added_denom_d.feedback


def test_fractions_subtraction_misconceptions() -> None:
    """Test fraction subtraction distractors."""
    f1 = Fraction(3, 4)
    f2 = Fraction(1, 2)
    correct_str = format_answer(f1 - f2, style="fraction")  # "1/4"

    distractors = get_fraction_add_sub_distractors(f1, f2, "-")
    assert_distractor_invariants(distractors, correct_str)

    tags = {d.misconception_tag for d in distractors}
    assert "added_denominators" in tags or "no_common_denominator" in tags


def test_fractions_add_unlike_denominators() -> None:
    """Test fraction addition with unlike denominators."""
    f1 = Fraction(1, 2)
    f2 = Fraction(1, 3)
    correct_str = format_answer(f1 + f2, style="fraction")  # "5/6"

    distractors = get_fraction_add_sub_distractors(f1, f2, "+")
    assert_distractor_invariants(distractors, correct_str)

    # (1 + 1)/(2 + 3) = 2/5
    added_denom_d = next(d for d in distractors if d.misconception_tag == "added_denominators")
    assert added_denom_d.text == "2/5"


# ============================================================================
# 2. Fractions: Multiplication & Division Tests
# ============================================================================

def test_fractions_division_misconceptions() -> None:
    """Test fraction division: multiplied_instead_of_inverting and flipped_wrong_fraction."""
    f1 = Fraction(3, 4)
    f2 = Fraction(2, 3)
    correct_str = format_answer(f1 / f2, style="fraction")  # "9/8"

    distractors = get_fraction_mult_div_distractors(f1, f2, "/")
    assert_distractor_invariants(distractors, correct_str)

    tags = {d.misconception_tag for d in distractors}
    assert "multiplied_instead_of_inverting" in tags
    assert "flipped_wrong_fraction" in tags

    # multiplied_instead_of_inverting: (3/4) * (2/3) = 6/12 = 1/2
    mult_d = next(d for d in distractors if d.misconception_tag == "multiplied_instead_of_inverting")
    assert mult_d.text == "1/2"
    assert "Keep, Change, Flip" in mult_d.feedback

    # flipped_wrong_fraction: (4/3) * (2/3) = 8/9
    flipped_d = next(d for d in distractors if d.misconception_tag == "flipped_wrong_fraction")
    assert flipped_d.text == "8/9"


def test_fractions_multiplication_misconceptions() -> None:
    """Test fraction multiplication distractors."""
    f1 = Fraction(3, 4)
    f2 = Fraction(2, 3)
    correct_str = format_answer(f1 * f2, style="fraction")  # "1/2"

    distractors = get_fraction_mult_div_distractors(f1, f2, "*")
    assert_distractor_invariants(distractors, correct_str)


# ============================================================================
# 3. Decimals: Operations & Place Value Tests
# ============================================================================

def test_decimals_misconceptions_addition() -> None:
    """Test decimal addition: misaligned_decimal_point and ignored_place_value."""
    d1 = Decimal("2.5")
    d2 = Decimal("0.15")
    correct_str = "2.65"

    distractors = get_decimal_distractors(d1, d2, "+", correct_str)
    assert_distractor_invariants(distractors, correct_str)

    tags = {d.misconception_tag for d in distractors}
    assert "misaligned_decimal_point" in tags or "ignored_place_value" in tags


def test_decimals_ignored_place_value() -> None:
    """Test ignored_place_value for 0.7 + 0.8 producing 0.15 instead of 1.5."""
    d1 = Decimal("0.7")
    d2 = Decimal("0.8")
    correct_str = "1.5"

    distractors = get_decimal_distractors(d1, d2, "+", correct_str)
    assert_distractor_invariants(distractors, correct_str)

    ignored_d = next(d for d in distractors if d.misconception_tag == "ignored_place_value")
    assert ignored_d.text == "0.15"
    assert "tenths and hundredths" in ignored_d.feedback


def test_decimals_dropped_trailing_zero_subtraction() -> None:
    """Test dropped_trailing_zero in subtraction: 5.0 - 2.35."""
    d1 = Decimal("5.0")
    d2 = Decimal("2.35")
    correct_str = "2.65"

    distractors = get_decimal_distractors(d1, d2, "-", correct_str)
    assert_distractor_invariants(distractors, correct_str)

    dropped_d = next(d for d in distractors if d.misconception_tag == "dropped_trailing_zero")
    assert dropped_d.text == "2.75"
    assert "placeholder zeros" in dropped_d.feedback


# ============================================================================
# 4. Ratios: Proportions & Scaling Tests
# ============================================================================

def test_ratio_misconceptions() -> None:
    """Test ratios: added_instead_of_scaled and inverted_ratio."""
    # Given ratio 2 : 3, first term scales to 6 (scale factor 3). Correct second term is 9.
    distractors = get_ratio_distractors(a=2, b=3, target_a=6)
    assert_distractor_invariants(distractors, "9")

    tags = {d.misconception_tag for d in distractors}
    assert "added_instead_of_scaled" in tags
    assert "inverted_ratio" in tags

    # added_instead_of_scaled: diff is 6 - 2 = 4; student adds 4 to 3 -> 7
    added_d = next(d for d in distractors if d.misconception_tag == "added_instead_of_scaled")
    assert added_d.text == "7"
    assert "multiplicative relationships" in added_d.feedback


# ============================================================================
# 5. Geometry: Area and Perimeter Tests
# ============================================================================

def test_geometry_rectangle_area_confused_with_perimeter() -> None:
    """Test rectangle area confused_area_perimeter: 5 x 3 -> area 15, perimeter 16."""
    distractors = get_geometry_distractors(
        shape="rectangle",
        dim1=5.0,
        dim2=3.0,
        target_metric="area",
    )
    assert_distractor_invariants(distractors, "15")

    confused_d = next(d for d in distractors if d.misconception_tag == "confused_area_perimeter")
    assert confused_d.text == "16"
    assert "Don't confuse area with perimeter" in confused_d.feedback


def test_geometry_rectangle_perimeter_confused_with_area() -> None:
    """Test rectangle perimeter confused_area_perimeter: 6 and 4 -> perimeter 20, area 24."""
    distractors = get_geometry_distractors(
        shape="rectangle",
        dim1=6.0,
        dim2=4.0,
        target_metric="perimeter",
    )
    assert_distractor_invariants(distractors, "20")

    confused_d = next(d for d in distractors if d.misconception_tag == "confused_area_perimeter")
    assert confused_d.text == "24"


def test_geometry_triangle_area_forgot_to_halve() -> None:
    """Test triangle area forgot_to_halve_triangle: base 6, height 4 -> correct 12, wrong 24."""
    distractors = get_geometry_distractors(
        shape="triangle",
        dim1=6.0,
        dim2=4.0,
        target_metric="area",
    )
    assert_distractor_invariants(distractors, "12")

    forgot_halve_d = next(d for d in distractors if d.misconception_tag == "forgot_to_halve_triangle")
    assert forgot_halve_d.text == "24"
    assert "A triangle is half of a rectangle" in forgot_halve_d.feedback


# ============================================================================
# 6. Additional Geometry Tests: Square & Parallelogram
# ============================================================================

def test_geometry_square_area_misconceptions() -> None:
    """Test square area distractors: side 5 -> correct 25, perimeter distractor 20."""
    distractors = get_geometry_distractors(
        shape="square",
        dim1=5.0,
        target_metric="area",
    )
    assert_distractor_invariants(distractors, "25")

    tags = {d.misconception_tag for d in distractors}
    assert "confused_area_perimeter" in tags
    assert "doubled_side" in tags

    confused_d = next(d for d in distractors if d.misconception_tag == "confused_area_perimeter")
    assert confused_d.text == "20"  # 4 * 5


def test_geometry_square_perimeter_misconceptions() -> None:
    """Test square perimeter distractors: side 4 -> correct 16."""
    distractors = get_geometry_distractors(
        shape="square",
        dim1=4.0,
        target_metric="perimeter",
    )
    # Correct perimeter is 16, area is also 16, so finalize_distractors ensures non-equal distractors
    assert_distractor_invariants(distractors, "16")

    # With side=6: perimeter=24, area=36
    distractors_6 = get_geometry_distractors(shape="square", dim1=6.0, target_metric="perimeter")
    assert_distractor_invariants(distractors_6, "24")
    tags_6 = {d.misconception_tag for d in distractors_6}
    assert "confused_area_perimeter" in tags_6
    confused_d = next(d for d in distractors_6 if d.misconception_tag == "confused_area_perimeter")
    assert confused_d.text == "36"


def test_geometry_parallelogram_area_misconceptions() -> None:
    """Test parallelogram area: base 8, height 5 -> correct 40, triangle halving error 20."""
    distractors = get_geometry_distractors(
        shape="parallelogram",
        dim1=8.0,
        dim2=5.0,
        target_metric="area",
    )
    assert_distractor_invariants(distractors, "40")

    tags = {d.misconception_tag for d in distractors}
    assert "halved_like_triangle" in tags
    halved_d = next(d for d in distractors if d.misconception_tag == "halved_like_triangle")
    assert halved_d.text == "20"


def test_geometry_parallelogram_perimeter_misconceptions() -> None:
    """Test parallelogram perimeter: base 10, side 4 -> correct 28."""
    distractors = get_parallelogram_distractors(
        base=10.0,
        height=3.0,
        side=4.0,
        target_metric="perimeter",
    )
    assert_distractor_invariants(distractors, "28")

    tags = {d.misconception_tag for d in distractors}
    assert "confused_area_perimeter" in tags or "forgot_other_sides" in tags


# ============================================================================
# 7. Number Theory: Factors & Multiples Tests (CBSE Class 6)
# ============================================================================

def test_factors_misconceptions() -> None:
    """Test factor questions: n=12, correct=6 -> distractor includes multiple 24."""
    distractors = get_factors_multiples_distractors(n=12, correct_answer=6, target_type="factors")
    assert_distractor_invariants(distractors, "6")

    tags = {d.misconception_tag for d in distractors}
    assert "confused_factor_multiple" in tags
    multiple_d = next(d for d in distractors if d.misconception_tag == "confused_factor_multiple")
    assert multiple_d.text == "24"


def test_multiples_misconceptions() -> None:
    """Test multiple questions: n=6, correct=18 -> distractor includes factor 2."""
    distractors = get_factors_multiples_distractors(n=6, correct_answer=18, target_type="multiples")
    assert_distractor_invariants(distractors, "18")

    tags = {d.misconception_tag for d in distractors}
    assert "confused_factor_multiple" in tags
    factor_d = next(d for d in distractors if d.misconception_tag == "confused_factor_multiple")
    assert factor_d.text == "2"


def test_prime_factors_misconceptions() -> None:
    """Test prime factor questions: n=12, correct=3 -> distractor includes composite factor 4 and non-prime 1."""
    distractors = get_factors_multiples_distractors(n=12, correct_answer=3, target_type="prime_factors")
    assert_distractor_invariants(distractors, "3")

    tags = {d.misconception_tag for d in distractors}
    assert "included_composite_factor" in tags
    assert "one_is_not_prime" in tags


# ============================================================================
# 8. Number Theory: LCM & GCD / HCF Tests (CBSE Class 6)
# ============================================================================

def test_lcm_misconceptions() -> None:
    """Test LCM: a=4, b=6 -> correct 12, GCD error 2, multiplication error 24."""
    distractors = get_lcm_gcd_distractors(a=4, b=6, target_type="lcm")
    assert_distractor_invariants(distractors, "12")

    tags = {d.misconception_tag for d in distractors}
    assert "confused_lcm_gcd" in tags
    assert "multiplied_numbers_instead_of_lcm" in tags

    gcd_d = next(d for d in distractors if d.misconception_tag == "confused_lcm_gcd")
    assert gcd_d.text == "2"

    mult_d = next(d for d in distractors if d.misconception_tag == "multiplied_numbers_instead_of_lcm")
    assert mult_d.text == "24"


def test_gcd_and_hcf_misconceptions() -> None:
    """Test GCD / HCF: a=12, b=18 -> correct 6, LCM error 36, non-greatest factor 2."""
    distractors = get_lcm_gcd_distractors(a=12, b=18, target_type="gcd")
    assert_distractor_invariants(distractors, "6")

    tags = {d.misconception_tag for d in distractors}
    assert "confused_lcm_gcd" in tags
    assert "chose_common_factor_not_greatest" in tags

    lcm_d = next(d for d in distractors if d.misconception_tag == "confused_lcm_gcd")
    assert lcm_d.text == "36"

    # Also test HCF alias
    hcf_distractors = get_lcm_gcd_distractors(a=12, b=18, target_type="hcf")
    assert_distractor_invariants(hcf_distractors, "6")

