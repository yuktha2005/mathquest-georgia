"""Comprehensive unit tests for mathematical verification parser and evaluator."""

from fractions import Fraction
import pytest

from app.services.verify import (
    AnswerStyle,
    DivisionByZeroError,
    InvalidExpressionError,
    MathVerificationError,
    evaluate,
    format_answer,
    verify_math_expression,
)


# ============================================================================
# Basic Arithmetic Operations
# ============================================================================

def test_integer_addition_and_subtraction() -> None:
    """Test integer addition and subtraction."""
    assert evaluate("5 + 7") == Fraction(12, 1)
    assert evaluate("15 - 8") == Fraction(7, 1)
    assert evaluate("10 - 20") == Fraction(-10, 1)


def test_fraction_addition() -> None:
    """Test addition of simple and like/unlike fractions."""
    assert evaluate("1/4 + 2/4") == Fraction(3, 4)
    assert evaluate("1/2 + 1/3") == Fraction(5, 6)
    assert evaluate("3/5 + 4/5") == Fraction(7, 5)


def test_fraction_subtraction() -> None:
    """Test subtraction of fractions."""
    assert evaluate("3/4 - 1/2") == Fraction(1, 4)
    assert evaluate("5/6 - 1/3") == Fraction(1, 2)
    assert evaluate("1/4 - 3/4") == Fraction(-1, 2)


def test_multiplication() -> None:
    """Test multiplication with integers and fractions."""
    assert evaluate("6 * 7") == Fraction(42, 1)
    assert evaluate("3/4 * 2/3") == Fraction(1, 2)
    assert evaluate("5 * 1/5") == Fraction(1, 1)


def test_division() -> None:
    """Test division with fractions and integers."""
    assert evaluate("12 / 4") == Fraction(3, 1)
    assert evaluate("3/4 / (1/2)") == Fraction(3, 2)
    assert evaluate("1/3 / (1/6)") == Fraction(2, 1)


# ============================================================================
# Decimals & Mixed Numbers
# ============================================================================

def test_decimal_numbers() -> None:
    """Test evaluating decimal numbers accurately without float rounding errors."""
    assert evaluate("2.5 + 1.25") == Fraction(15, 4)
    assert evaluate("0.75 * 4") == Fraction(3, 1)
    assert evaluate("3.6 - 1.2") == Fraction(12, 5)
    assert evaluate("0.1 + 0.2") == Fraction(3, 10)


def test_mixed_numbers_addition_and_subtraction() -> None:
    """Test mixed numbers parsing and arithmetic."""
    assert evaluate("2 1/3 + 1 1/3") == Fraction(11, 3)
    assert evaluate("1 1/2 + 2 1/4") == Fraction(15, 4)
    assert evaluate("3 1/4 - 1 1/2") == Fraction(7, 4)


def test_mixed_numbers_multiplication_and_division() -> None:
    """Test mixed numbers with multiplication and division."""
    assert evaluate("1 1/2 * 2 2/3") == Fraction(4, 1)
    assert evaluate("2 1/3 / (1/3)") == Fraction(7, 1)


# ============================================================================
# Precedence, Parentheses & Unary Operators
# ============================================================================

def test_order_of_operations_pemdas() -> None:
    """Test PEMDAS operator precedence."""
    assert evaluate("2 + 3 * 4") == Fraction(14, 1)
    assert evaluate("10 - 4 / 2") == Fraction(8, 1)
    assert evaluate("20 / 4 * 2") == Fraction(10, 1)  # Left-associative


def test_nested_parentheses() -> None:
    """Test complex nested parentheses."""
    assert evaluate("(2 + 3) * 4") == Fraction(20, 1)
    assert evaluate("((2 + 3) * (4 - 1)) / 5") == Fraction(3, 1)
    assert evaluate("(10 + (2 * (5 - 1))) / 3") == Fraction(6, 1)


def test_unary_signs_and_negatives() -> None:
    """Test unary plus, unary minus, and negative expressions."""
    assert evaluate("-5 + 8") == Fraction(3, 1)
    assert evaluate("-(2 + 3)") == Fraction(-5, 1)
    assert evaluate("-2 1/3") == Fraction(-7, 3)
    assert evaluate("5 * -2") == Fraction(-10, 1)


def test_unicode_operators() -> None:
    """Test support for unicode math symbols (×, ÷, −)."""
    assert evaluate("6 × 7") == Fraction(42, 1)
    assert evaluate("15 ÷ 3") == Fraction(5, 1)
    assert evaluate("10 − 4") == Fraction(6, 1)


# ============================================================================
# Division by Zero Errors
# ============================================================================

def test_division_by_zero_direct() -> None:
    """Test division by zero raises DivisionByZeroError."""
    with pytest.raises(DivisionByZeroError) as exc_info:
        evaluate("5 / 0")
    assert "Division by zero" in str(exc_info.value)


def test_division_by_zero_in_parentheses() -> None:
    """Test division by expression that evaluates to zero."""
    with pytest.raises(DivisionByZeroError):
        evaluate("10 / (5 - 5)")


def test_division_by_zero_in_mixed_number() -> None:
    """Test mixed number with zero denominator raises DivisionByZeroError."""
    with pytest.raises(DivisionByZeroError):
        evaluate("2 1/0")


# ============================================================================
# Malicious Input & Injection Protection (No eval())
# ============================================================================

def test_malicious_import_blocked() -> None:
    """Test code injection via __import__ is immediately rejected at tokenizer level."""
    with pytest.raises(InvalidExpressionError) as exc_info:
        evaluate("__import__('os').system('calc')")
    assert "Unexpected character" in str(exc_info.value)


def test_malicious_eval_blocked() -> None:
    """Test eval keyword is rejected."""
    with pytest.raises(InvalidExpressionError):
        evaluate("eval('2 + 2')")


def test_malicious_builtin_blocked() -> None:
    """Test Python builtins and variable names are rejected."""
    with pytest.raises(InvalidExpressionError):
        evaluate("open('/etc/passwd')")


# ============================================================================
# Syntax Errors & Invalid Input Handling
# ============================================================================

def test_empty_or_whitespace_expression() -> None:
    """Test empty string or whitespace-only raises InvalidExpressionError."""
    with pytest.raises(InvalidExpressionError):
        evaluate("")
    with pytest.raises(InvalidExpressionError):
        evaluate("   ")


def test_unbalanced_parentheses() -> None:
    """Test unclosed or mismatched parentheses."""
    with pytest.raises(InvalidExpressionError):
        evaluate("(2 + 3")
    with pytest.raises(InvalidExpressionError):
        evaluate("2 + 3)")
    with pytest.raises(InvalidExpressionError):
        evaluate("()")


def test_trailing_operator() -> None:
    """Test trailing operators raise InvalidExpressionError."""
    with pytest.raises(InvalidExpressionError):
        evaluate("5 + ")
    with pytest.raises(InvalidExpressionError):
        evaluate("* 4")


def test_consecutive_numbers_without_operator() -> None:
    """Test two numbers without operator raises InvalidExpressionError."""
    with pytest.raises(InvalidExpressionError):
        evaluate("5 10")


# ============================================================================
# Answer Formatting: format_answer
# ============================================================================

def test_format_answer_simplified_fraction() -> None:
    """Test formatting as simplified fraction."""
    assert format_answer(Fraction(3, 4), style="fraction") == "3/4"
    assert format_answer(Fraction(10, 4), style="fraction") == "5/2"
    assert format_answer(Fraction(6, 2), style="fraction") == "3"
    assert format_answer(Fraction(-3, 4), style=AnswerStyle.FRACTION) == "-3/4"


def test_format_answer_mixed_number() -> None:
    """Test formatting as mixed number."""
    assert format_answer(Fraction(7, 3), style="mixed") == "2 1/3"
    assert format_answer(Fraction(11, 4), style="mixed") == "2 3/4"
    assert format_answer(Fraction(3, 4), style="mixed") == "3/4"
    assert format_answer(Fraction(5, 1), style="mixed") == "5"
    assert format_answer(Fraction(-7, 3), style=AnswerStyle.MIXED) == "-2 1/3"
    assert format_answer(Fraction(0, 1), style="mixed") == "0"


def test_format_answer_decimal() -> None:
    """Test formatting as decimal."""
    assert format_answer(Fraction(3, 4), style="decimal") == "0.75"
    assert format_answer(Fraction(5, 2), style="decimal") == "2.5"
    assert format_answer(Fraction(4, 1), style="decimal") == "4"
    assert format_answer(Fraction(1, 3), style=AnswerStyle.DECIMAL) == "0.3333"


def test_format_answer_invalid_style() -> None:
    """Test unknown style raises ValueError."""
    with pytest.raises(ValueError):
        format_answer(Fraction(1, 2), style="roman_numerals")


# ============================================================================
# verify_math_expression Helper
# ============================================================================

def test_verify_math_expression_helper() -> None:
    """Test verify_math_expression returns boolean safely."""
    assert verify_math_expression("3/4 + 1/2") is True
    assert verify_math_expression("2 1/3 * 3") is True
    assert verify_math_expression("5 / 0") is False
    assert verify_math_expression("__import__('os')") is False
    assert verify_math_expression("") is False
