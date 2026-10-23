"""Curated mathematical misconception library and distractor generator.

Enforces Rule 3: Multiple-choice distractors must always be generated in code
using a curated misconception library—never hallucinated by an LLM.

Supported Topics & Misconceptions:
- Fractions (Add/Subtract):
    * added_denominators: (a+c)/(b+d)
    * no_common_denominator: adding/subtracting numerators over an unconverted denominator
    * forgot_to_simplify: unreduced fraction equivalent to the correct answer
- Fractions (Multiply/Divide):
    * multiplied_instead_of_inverting: multiplying straight across during division
    * flipped_wrong_fraction: inverting the dividend instead of divisor
- Decimals:
    * misaligned_decimal_point: aligning numbers on the right without lining up decimal points
    * ignored_place_value: treating digits after the decimal point as standalone whole numbers
    * dropped_trailing_zero: omitting placeholder zeros during subtraction/borrowing
- Ratios:
    * added_instead_of_scaled: using additive reasoning instead of multiplicative scaling
    * inverted_ratio: flipping the antecedent and consequent
- Geometry (Area/Perimeter):
    * confused_area_perimeter: computing perimeter when area is requested (or vice-versa)
    * forgot_to_halve_triangle: computing base * height for triangle area without dividing by 2
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
import math
from typing import Literal

from app.services.verify import format_answer


@dataclass(frozen=True)
class MisconceptionDistractor:
    """A generated multiple-choice distractor with a diagnostic tag and feedback."""
    text: str
    misconception_tag: str
    feedback: str


def _clean_num(val: float | Decimal) -> str:
    """Format a float or Decimal cleanly without unnecessary trailing decimals."""
    if isinstance(val, Decimal):
        if val == val.to_integral():
            return str(int(val))
        s = f"{val:f}"
        return s.rstrip("0").rstrip(".") if "." in s else s
    if float(val).is_integer():
        return str(int(val))
    return f"{val:.4f}".rstrip("0").rstrip(".")


def finalize_distractors(
    candidates: list[MisconceptionDistractor],
    correct_answer_str: str,
    fallbacks: list[MisconceptionDistractor],
    target_count: int = 3,
) -> list[MisconceptionDistractor]:
    """Ensure distractors are unique, never equal the correct answer, and always return target_count."""
    selected: list[MisconceptionDistractor] = []
    seen_texts: set[str] = {correct_answer_str.strip()}

    # 1. Add valid candidate misconceptions
    for cand in candidates:
        cand_text = cand.text.strip()
        if cand_text and cand_text not in seen_texts:
            seen_texts.add(cand_text)
            selected.append(cand)
            if len(selected) == target_count:
                return selected

    # 2. Add domain-specific fallbacks
    for fb in fallbacks:
        fb_text = fb.text.strip()
        if fb_text and fb_text not in seen_texts:
            seen_texts.add(fb_text)
            selected.append(fb)
            if len(selected) == target_count:
                return selected

    # 3. Emergency fallback generator if severe collisions occurred
    counter = 1
    while len(selected) < target_count:
        alt_text = f"{correct_answer_str}+{counter}"
        # If correct answer is a number, create clean numeric offset
        try:
            if "/" in correct_answer_str:
                num, den = map(int, correct_answer_str.split("/"))
                alt_text = f"{num + counter}/{den}"
            else:
                num = float(correct_answer_str)
                alt_text = _clean_num(num + counter)
        except Exception:
            alt_text = f"Option {counter}"

        if alt_text not in seen_texts:
            seen_texts.add(alt_text)
            selected.append(
                MisconceptionDistractor(
                    text=alt_text,
                    misconception_tag="calculation_error",
                    feedback="Double-check your calculations and operations step-by-step.",
                )
            )
        counter += 1

    return selected[:target_count]


# ============================================================================
# 1. Fractions: Addition and Subtraction
# ============================================================================

def get_fraction_add_sub_distractors(
    f1: Fraction,
    f2: Fraction,
    op: Literal["+", "-"],
    format_style: str = "fraction",
    raw_operands: tuple[int, int, int, int] | None = None,
) -> list[MisconceptionDistractor]:
    """Generate 3 distractors for fraction addition or subtraction.
    
    Args:
        f1: First fraction operand.
        f2: Second fraction operand.
        op: Operation '+' or '-'.
        format_style: Output style ('fraction', 'mixed', or 'decimal').
        raw_operands: Optional (a, b, c, d) representing unreduced input operands.
    """
    correct_val = f1 + f2 if op == "+" else f1 - f2
    correct_str = format_answer(correct_val, style=format_style)

    if raw_operands:
        a, b, c, d = raw_operands
    else:
        a, b = f1.numerator, f1.denominator
        c, d = f2.numerator, f2.denominator

    candidates: list[MisconceptionDistractor] = []

    # Misconception 1: added_denominators ((a + c) / (b + d))
    if op == "+":
        num1 = a + c
        den1 = b + d
        text1 = format_answer(Fraction(num1, den1), style=format_style)
        fb1 = (
            "Denominators show the size of the parts, not the count. "
            "Never add denominators together! Find a common denominator first, then add only the numerators."
        )
    else:
        num1 = abs(a - c)
        den1 = abs(b - d) if b != d else (b + d)
        if den1 == 0:
            den1 = b + d
        text1 = format_answer(Fraction(num1, den1), style=format_style)
        fb1 = (
            "When subtracting fractions, keep the common denominator. "
            "Do not subtract or add the denominators together."
        )
    candidates.append(
        MisconceptionDistractor(
            text=text1,
            misconception_tag="added_denominators",
            feedback=fb1,
        )
    )

    # Misconception 2: no_common_denominator (add/subtract numerators over unconverted denominator)
    num2 = (a + c) if op == "+" else (a - c)
    den2 = b if b != d else (b + 1)
    text2 = format_answer(Fraction(num2, den2), style=format_style)
    fb2 = (
        "You cannot add or subtract fractions with different denominators directly. "
        "Convert both fractions to have equivalent common denominators first!"
    )
    candidates.append(
        MisconceptionDistractor(
            text=text2,
            misconception_tag="no_common_denominator",
            feedback=fb2,
        )
    )

    # Misconception 3: forgot_to_simplify (unsimplified equivalent fraction)
    # Multiply numerator and denominator by 2 to construct an unreduced equivalent
    if correct_val.denominator > 1:
        unsimplified_text = f"{correct_val.numerator * 2}/{correct_val.denominator * 2}"
    else:
        unsimplified_text = f"{correct_val.numerator * 2}/2"
    candidates.append(
        MisconceptionDistractor(
            text=unsimplified_text,
            misconception_tag="forgot_to_simplify",
            feedback=(
                "Your calculation was on the right track, but don't forget to simplify "
                "your fraction to its lowest terms by dividing by the greatest common factor."
            ),
        )
    )

    # Domain Fallbacks
    opposite_op = "-" if op == "+" else "+"
    opp_val = f1 - f2 if op == "+" else f1 + f2
    fallbacks = [
        MisconceptionDistractor(
            text=format_answer(opp_val, style=format_style),
            misconception_tag="wrong_operation",
            feedback=f"Check the operation symbol! You { 'subtracted' if op == '+' else 'added' } instead.",
        ),
        MisconceptionDistractor(
            text=format_answer(Fraction(correct_val.numerator + 1, correct_val.denominator), style=format_style),
            misconception_tag="calculation_error",
            feedback="You made a small addition or subtraction error in the numerator.",
        ),
    ]

    return finalize_distractors(candidates, correct_str, fallbacks)


# ============================================================================
# 2. Fractions: Multiplication and Division
# ============================================================================

def get_fraction_mult_div_distractors(
    f1: Fraction,
    f2: Fraction,
    op: Literal["*", "/"],
    format_style: str = "fraction",
) -> list[MisconceptionDistractor]:
    """Generate 3 distractors for fraction multiplication or division."""
    if op == "/" and f2 == 0:
        raise ValueError("Cannot generate division distractors with divisor equal to 0.")

    correct_val = f1 * f2 if op == "*" else f1 / f2
    correct_str = format_answer(correct_val, style=format_style)

    candidates: list[MisconceptionDistractor] = []

    if op == "/":
        # Misconception 1: multiplied_instead_of_inverting ((a*c)/(b*d))
        mult_val = f1 * f2
        candidates.append(
            MisconceptionDistractor(
                text=format_answer(mult_val, style=format_style),
                misconception_tag="multiplied_instead_of_inverting",
                feedback=(
                    "When dividing fractions, remember 'Keep, Change, Flip'—keep the first fraction, "
                    "change division to multiplication, and flip the second fraction before multiplying."
                ),
            )
        )

        # Misconception 2: flipped_wrong_fraction (flipped dividend instead of divisor: (1/f1) * f2)
        if f1 != 0:
            flipped_wrong_val = (1 / f1) * f2
            candidates.append(
                MisconceptionDistractor(
                    text=format_answer(flipped_wrong_val, style=format_style),
                    misconception_tag="flipped_wrong_fraction",
                    feedback=(
                        "Be careful which fraction you flip! Keep the first fraction as it is, "
                        "and only invert the second fraction (the divisor)."
                    ),
                )
            )

        # Misconception 3: added_instead_of_multiplied
        candidates.append(
            MisconceptionDistractor(
                text=format_answer(f1 + f2, style=format_style),
                misconception_tag="wrong_operation",
                feedback="Check the operation symbol! You added the fractions instead of dividing.",
            )
        )
    else:  # op == "*"
        # Misconception 1: multiplied_instead_of_inverting / inverted while multiplying (f1 / f2)
        if f2 != 0:
            div_val = f1 / f2
            candidates.append(
                MisconceptionDistractor(
                    text=format_answer(div_val, style=format_style),
                    misconception_tag="multiplied_instead_of_inverting",
                    feedback=(
                        "When multiplying fractions, multiply straight across (numerator × numerator and "
                        "denominator × denominator). Do not flip the second fraction!"
                    ),
                )
            )

        # Misconception 2: flipped_wrong_fraction (flipped first fraction: (1/f1) * f2)
        if f1 != 0:
            flipped_val = (1 / f1) * f2
            candidates.append(
                MisconceptionDistractor(
                    text=format_answer(flipped_val, style=format_style),
                    misconception_tag="flipped_wrong_fraction",
                    feedback="Do not invert any fractions when multiplying. Simply multiply straight across.",
                )
            )

        # Misconception 3: forgot_to_simplify
        if correct_val.denominator > 1:
            unsimplified_text = f"{correct_val.numerator * 2}/{correct_val.denominator * 2}"
        else:
            unsimplified_text = f"{correct_val.numerator * 2}/2"
        candidates.append(
            MisconceptionDistractor(
                text=unsimplified_text,
                misconception_tag="forgot_to_simplify",
                feedback="Don't forget to simplify your product to lowest terms!",
            )
        )

    # Fallbacks
    fallbacks = [
        MisconceptionDistractor(
            text=format_answer(1 / correct_val if correct_val != 0 else Fraction(1, 2), style=format_style),
            misconception_tag="inverted_result",
            feedback="The numerator and denominator of the final answer were inverted.",
        ),
        MisconceptionDistractor(
            text=format_answer(Fraction(correct_val.numerator + 1, correct_val.denominator), style=format_style),
            misconception_tag="calculation_error",
            feedback="Check your multiplication of the numerators and denominators.",
        ),
    ]

    return finalize_distractors(candidates, correct_str, fallbacks)


# ============================================================================
# 3. Decimals: Operations & Place Value
# ============================================================================

def get_decimal_distractors(
    d1: Decimal | float | str,
    d2: Decimal | float | str,
    op: Literal["+", "-", "*"],
    correct_answer: Decimal | float | str,
) -> list[MisconceptionDistractor]:
    """Generate 3 distractors for decimal operations."""
    dec1 = Decimal(str(d1))
    dec2 = Decimal(str(d2))
    correct_dec = Decimal(str(correct_answer))
    correct_str = _clean_num(correct_dec)

    candidates: list[MisconceptionDistractor] = []

    # Misconception 1: misaligned_decimal_point
    # Simulates aligning numbers on the right without lining up the decimal points
    # e.g. for 2.5 + 0.15: aligns 25 and 15 -> 40 -> 0.40 or 4.0
    str1 = str(dec1).replace("-", "")
    str2 = str(dec2).replace("-", "")
    digits1 = str1.replace(".", "")
    digits2 = str2.replace(".", "")

    try:
        int1, int2 = int(digits1), int(digits2)
        raw_res = int1 + int2 if op == "+" else (int1 - int2 if op == "-" else int1 * int2)
        # Place decimal based on rightmost alignment
        dec_places1 = len(str1.split(".")[1]) if "." in str1 else 0
        dec_places2 = len(str2.split(".")[1]) if "." in str2 else 0
        misaligned_places = min(dec_places1, dec_places2) or max(dec_places1, dec_places2)
        misaligned_val = Decimal(raw_res) / Decimal(10 ** misaligned_places)
        candidates.append(
            MisconceptionDistractor(
                text=_clean_num(misaligned_val),
                misconception_tag="misaligned_decimal_point",
                feedback=(
                    "Always line up the decimal points vertically before operating. "
                    "Each place value (ones, tenths, hundredths) must line up with the same place value!"
                ),
            )
        )
    except Exception:
        pass

    # Misconception 2: ignored_place_value
    # Treating decimals as standalone integers without regrouping (e.g. 0.7 + 0.8 = 0.15)
    whole1, frac1 = int(dec1), abs(dec1 - int(dec1))
    whole2, frac2 = int(dec2), abs(dec2 - int(dec2))
    s_frac1 = str(frac1).split(".")[1] if "." in str(frac1) else "0"
    s_frac2 = str(frac2).split(".")[1] if "." in str(frac2) else "0"

    try:
        if op == "+":
            int_frac_sum = int(s_frac1) + int(s_frac2)
            ignored_val = Decimal(f"{whole1 + whole2}.{int_frac_sum}")
        elif op == "-":
            int_frac_diff = abs(int(s_frac1) - int(s_frac2))
            ignored_val = Decimal(f"{abs(whole1 - whole2)}.{int_frac_diff}")
        else:
            ignored_val = Decimal(f"{whole1 * whole2}.{int(s_frac1) * int(s_frac2)}")

        candidates.append(
            MisconceptionDistractor(
                text=_clean_num(ignored_val),
                misconception_tag="ignored_place_value",
                feedback=(
                    "Digits after the decimal point represent tenths and hundredths, not whole numbers. "
                    "Remember to regroup (carry over) when a column reaches 10 tenths!"
                ),
            )
        )
    except Exception:
        pass

    # Misconception 3: dropped_trailing_zero
    # For subtraction without adding placeholder zeros (e.g. 5.0 - 2.35 = 2.75 or 3.35)
    if op == "-":
        if dec_places2 > dec_places1:
            dec1_part = Decimal(f"{int(dec1)}.{s_frac1[0] if s_frac1 != '0' else '0'}")
            dec2_part = Decimal(f"{int(dec2)}.{s_frac2[0]}")
            diff_part = dec1_part - dec2_part
            excess = s_frac2[1:] if len(s_frac2) > 1 else ""
            dropped_val = Decimal(f"{diff_part}{excess}")
        else:
            dropped_val = Decimal(f"{int(dec1) - int(dec2)}.{s_frac2}")

        if _clean_num(dropped_val) == _clean_num(ignored_val):
            dropped_val = correct_dec + Decimal("0.1")

        feedback3 = (
            "When subtracting decimals, annex placeholder zeros (like writing 5.0 as 5.00) "
            "so you can borrow and subtract accurately across all columns."
        )
    else:
        # Dropping a zero on trailing tenths/hundredths e.g. 0.50 + 0.02 = 0.52
        dropped_val = correct_dec * Decimal("10")
        if _clean_num(dropped_val) == _clean_num(ignored_val):
            dropped_val = correct_dec / Decimal("10")
        feedback3 = "Keep track of placeholder zeros so digits stay in their correct decimal place."

    candidates.append(
        MisconceptionDistractor(
            text=_clean_num(dropped_val),
            misconception_tag="dropped_trailing_zero",
            feedback=feedback3,
        )
    )

    # Fallbacks
    fallbacks = [
        MisconceptionDistractor(
            text=_clean_num(dec1 - dec2 if op == "+" else dec1 + dec2),
            misconception_tag="wrong_operation",
            feedback=f"Check your operation sign! You { 'subtracted' if op == '+' else 'added' } instead.",
        ),
        MisconceptionDistractor(
            text=_clean_num(correct_dec + Decimal("0.1")),
            misconception_tag="calculation_error",
            feedback="You made a small calculation error in the tenths place.",
        ),
        MisconceptionDistractor(
            text=_clean_num(correct_dec / Decimal("10")),
            misconception_tag="decimal_place_shift",
            feedback="The decimal point was placed one position too far to the left.",
        ),
    ]

    return finalize_distractors(candidates, correct_str, fallbacks)


# ============================================================================
# 4. Ratios: Proportions & Scaling
# ============================================================================

def get_ratio_distractors(
    a: int,
    b: int,
    target_a: int | None = None,
    target_b: int | None = None,
    scale_factor: int | float | None = None,
) -> list[MisconceptionDistractor]:
    """Generate 3 distractors for equivalent ratios (a : b = target_a : target_b).

    Assumes one of target_a or target_b is the unknown to solve for.
    If target_a is provided, target_b is calculated, and vice versa.
    """
    if scale_factor is None:
        if target_a is not None and a != 0:
            scale_factor = target_a / a
        elif target_b is not None and b != 0:
            scale_factor = target_b / b
        else:
            scale_factor = 2

    # Determining what is being solved: target_b or target_a
    if target_a is not None and target_b is None:
        solving_for = "b"
        correct_val = b * scale_factor
        known_target = target_a
        known_orig = a
        other_orig = b
    else:
        solving_for = "a"
        if target_b is None:
            target_b = int(b * scale_factor)
        correct_val = a * scale_factor
        known_target = target_b
        known_orig = b
        other_orig = a

    correct_str = _clean_num(correct_val)
    candidates: list[MisconceptionDistractor] = []

    # Misconception 1: added_instead_of_scaled
    # Student computes difference (known_target - known_orig) and adds to other_orig
    diff = known_target - known_orig
    additive_val = other_orig + diff
    candidates.append(
        MisconceptionDistractor(
            text=_clean_num(additive_val),
            misconception_tag="added_instead_of_scaled",
            feedback=(
                "Ratios represent multiplicative relationships, not additive! "
                "Multiply or divide both terms by the same scale factor instead of adding the difference."
            ),
        )
    )

    # Misconception 2: inverted_ratio
    # Student inverts the ratio multiplier (e.g. multiplies by orig/target instead of target/orig)
    if scale_factor != 0:
        inverted_val = other_orig / scale_factor
        candidates.append(
            MisconceptionDistractor(
                text=_clean_num(inverted_val),
                misconception_tag="inverted_ratio",
                feedback=(
                    "Check the order of your ratio terms! Make sure you are scaling in the correct direction "
                    "without flipping the antecedent and consequent."
                ),
            )
        )

    # Misconception 3: scaled_only_one_term or off-by-one scale factor
    off_scale_val = other_orig * (scale_factor + 1)
    candidates.append(
        MisconceptionDistractor(
            text=_clean_num(off_scale_val),
            misconception_tag="incorrect_scale_factor",
            feedback="Double-check the scale factor used to convert between equivalent ratios.",
        )
    )

    # Fallbacks
    fallbacks = [
        MisconceptionDistractor(
            text=_clean_num(other_orig * (scale_factor - 1) if scale_factor > 1 else other_orig * 2),
            misconception_tag="incorrect_scale_factor",
            feedback="Make sure to multiply both terms of the ratio by the exact same scale factor.",
        ),
        MisconceptionDistractor(
            text=_clean_num(correct_val + 1),
            misconception_tag="calculation_error",
            feedback="Check your multiplication when calculating the equivalent ratio.",
        ),
    ]

    return finalize_distractors(candidates, correct_str, fallbacks)


# ============================================================================
# 5. Geometry: Area and Perimeter
# ============================================================================

def get_geometry_distractors(
    shape: Literal["rectangle", "triangle"],
    dim1: float,
    dim2: float,
    target_metric: Literal["area", "perimeter"],
) -> list[MisconceptionDistractor]:
    """Generate 3 distractors for geometry area or perimeter problems.

    Args:
        shape: "rectangle" (dim1=length, dim2=width) or "triangle" (dim1=base, dim2=height)
        dim1: First dimension (length or base)
        dim2: Second dimension (width or height)
        target_metric: "area" or "perimeter"
    """
    candidates: list[MisconceptionDistractor] = []

    if shape == "rectangle":
        length, width = dim1, dim2
        correct_val = (length * width) if target_metric == "area" else (2 * (length + width))
        correct_str = _clean_num(correct_val)

        # Misconception 1: confused_area_perimeter
        if target_metric == "area":
            perimeter_val = 2 * (length + width)
            candidates.append(
                MisconceptionDistractor(
                    text=_clean_num(perimeter_val),
                    misconception_tag="confused_area_perimeter",
                    feedback=(
                        "Don't confuse area with perimeter! Perimeter is the boundary distance (2 × length + 2 × width). "
                        "Area is the space inside (length × width)."
                    ),
                )
            )
            # Misconception 2: added_dimensions (l + w instead of l * w)
            candidates.append(
                MisconceptionDistractor(
                    text=_clean_num(length + width),
                    misconception_tag="added_dimensions",
                    feedback="Adding length and width gives only half of the perimeter, not the area. Multiply length × width for area.",
                )
            )
        else:  # target_metric == "perimeter"
            area_val = length * width
            candidates.append(
                MisconceptionDistractor(
                    text=_clean_num(area_val),
                    misconception_tag="confused_area_perimeter",
                    feedback=(
                        "Don't confuse perimeter with area! Area is length × width. "
                        "Perimeter is the distance all the way around the outside (2 × length + 2 × width)."
                    ),
                )
            )
            # Misconception 2: forgot_to_double (l + w instead of 2*(l + w))
            candidates.append(
                MisconceptionDistractor(
                    text=_clean_num(length + width),
                    misconception_tag="forgot_other_sides",
                    feedback="A rectangle has 4 sides! Don't forget to include all 4 sides when calculating perimeter.",
                )
            )

        # Misconception 3: squared_one_dimension
        candidates.append(
            MisconceptionDistractor(
                text=_clean_num(length ** 2),
                misconception_tag="incorrect_formula",
                feedback="Only squares have area = side × side. For rectangles, multiply length × width.",
            )
        )

        fallbacks = [
            MisconceptionDistractor(
                text=_clean_num(correct_val + 2),
                misconception_tag="calculation_error",
                feedback="Check your arithmetic when calculating rectangle measurements.",
            ),
            MisconceptionDistractor(
                text=_clean_num(correct_val * 2),
                misconception_tag="doubled_measurement",
                feedback="Make sure you did not accidentally double the final measurement.",
            ),
        ]

    else:  # shape == "triangle"
        base, height = dim1, dim2
        correct_val = 0.5 * base * height
        correct_str = _clean_num(correct_val)

        # Misconception 1: forgot_to_halve_triangle (base * height)
        forgot_halve_val = base * height
        candidates.append(
            MisconceptionDistractor(
                text=_clean_num(forgot_halve_val),
                misconception_tag="forgot_to_halve_triangle",
                feedback=(
                    "A triangle is half of a rectangle with the same base and height. "
                    "Don't forget to multiply by 1/2 (or divide base × height by 2)!"
                ),
            )
        )

        # Misconception 2: confused_area_perimeter / added dimensions
        added_val = base + height
        candidates.append(
            MisconceptionDistractor(
                text=_clean_num(added_val),
                misconception_tag="confused_area_perimeter",
                feedback="To find the area of a triangle, multiply base × height ÷ 2. Do not just add the dimensions.",
            )
        )

        # Misconception 3: halved_both_dimensions ((base/2) * (height/2) = (b*h)/4)
        quartered_val = 0.25 * base * height
        candidates.append(
            MisconceptionDistractor(
                text=_clean_num(quartered_val),
                misconception_tag="halved_both_dimensions",
                feedback="Divide by 2 only once when finding triangle area (base × height ÷ 2), not twice.",
            )
        )

        fallbacks = [
            MisconceptionDistractor(
                text=_clean_num(correct_val + 1),
                misconception_tag="calculation_error",
                feedback="Check your multiplication and division steps carefully.",
            ),
            MisconceptionDistractor(
                text=_clean_num(correct_val + base),
                misconception_tag="added_side",
                feedback="Review the triangle area formula: A = 1/2 × base × height.",
            ),
        ]

    return finalize_distractors(candidates, correct_str, fallbacks)
