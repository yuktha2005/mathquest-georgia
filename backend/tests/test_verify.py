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
    gcd,
    get_factors,
    get_multiples,
    get_prime_factors,
    is_coprime,
    is_prime,
    lcm,
    parallelogram_area,
    parallelogram_perimeter,
    rectangle_area,
    rectangle_perimeter,
    square_area,
    square_perimeter,
    triangle_area,
    triangle_perimeter,
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


# ============================================================================
# Additional Security & AST Safety Tests
# ============================================================================

def test_advanced_malicious_code_injection_blocked() -> None:
    """Ensure arbitrary code execution exploits are blocked at tokenizer level without eval()."""
    malicious_payloads = [
        "exec('import sys; sys.exit()')",
        "compile('2+2', '', 'eval')",
        "getattr(__builtins__, 'eval')",
        "'string literal'",
        '"quoted expression"',
        "[1, 2, 3]",
        "{'a': 1}",
        "5; 10",
        "5 & 3",
        "5 | 2",
        "~5",
        "2 ** 1000",
        "lambda x: x + 1",
    ]
    for payload in malicious_payloads:
        with pytest.raises(InvalidExpressionError):
            evaluate(payload)


# ============================================================================
# Geometry Verification Tests
# ============================================================================

def test_geometry_rectangle_calculations() -> None:
    """Test deterministic calculation of rectangle area and perimeter."""
    assert rectangle_area(5, 3) == Fraction(15, 1)
    assert rectangle_area("2.5", "4") == Fraction(10, 1)
    assert rectangle_area(Fraction(3, 4), Fraction(2, 3)) == Fraction(1, 2)
    assert rectangle_perimeter(5, 3) == Fraction(16, 1)
    assert rectangle_perimeter("2.5", "1.5") == Fraction(8, 1)
    assert rectangle_perimeter(Fraction(1, 2), Fraction(3, 4)) == Fraction(5, 2)


def test_geometry_square_calculations() -> None:
    """Test deterministic calculation of square area and perimeter."""
    assert square_area(6) == Fraction(36, 1)
    assert square_area("1.5") == Fraction(9, 4)
    assert square_area(Fraction(3, 2)) == Fraction(9, 4)
    assert square_perimeter(6) == Fraction(24, 1)
    assert square_perimeter("2.5") == Fraction(10, 1)
    assert square_perimeter(Fraction(3, 4)) == Fraction(3, 1)


def test_geometry_triangle_calculations() -> None:
    """Test deterministic calculation of triangle area and perimeter."""
    assert triangle_area(8, 5) == Fraction(20, 1)
    assert triangle_area("3.5", 4) == Fraction(7, 1)
    assert triangle_area(Fraction(4, 3), Fraction(3, 2)) == Fraction(1, 1)
    assert triangle_perimeter(3, 4, 5) == Fraction(12, 1)
    assert triangle_perimeter("2.5", "3.5", "4.0") == Fraction(10, 1)


def test_geometry_parallelogram_calculations() -> None:
    """Test deterministic calculation of parallelogram area and perimeter."""
    assert parallelogram_area(10, 4) == Fraction(40, 1)
    assert parallelogram_area("6.5", 2) == Fraction(13, 1)
    assert parallelogram_area(Fraction(5, 2), Fraction(4, 5)) == Fraction(2, 1)
    assert parallelogram_perimeter(8, 5) == Fraction(26, 1)
    assert parallelogram_perimeter("4.5", "2.5") == Fraction(14, 1)


def test_geometry_invalid_inputs_rejected() -> None:
    """Test that zero or negative dimensions raise InvalidExpressionError."""
    with pytest.raises(InvalidExpressionError):
        rectangle_area(-5, 3)
    with pytest.raises(InvalidExpressionError):
        rectangle_area(5, 0)
    with pytest.raises(InvalidExpressionError):
        square_area(-2)
    with pytest.raises(InvalidExpressionError):
        square_perimeter(0)
    with pytest.raises(InvalidExpressionError):
        triangle_area(0, 5)
    with pytest.raises(InvalidExpressionError):
        triangle_perimeter(3, -4, 5)
    with pytest.raises(InvalidExpressionError):
        parallelogram_area(-10, 4)
    with pytest.raises(InvalidExpressionError):
        parallelogram_perimeter(8, 0)


# ============================================================================
# Number Theory Verification Tests (CBSE Class 6)
# ============================================================================

def test_is_prime_correctness() -> None:
    """Test primality test against known primes and composite numbers."""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
    for p in primes:
        assert is_prime(p) is True, f"Expected {p} to be prime"

    composites = [-5, 0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 21, 25, 27, 49, 100]
    for c in composites:
        assert is_prime(c) is False, f"Expected {c} to not be prime"


def test_is_prime_type_errors() -> None:
    """Test is_prime rejects non-integer types safely."""
    with pytest.raises(InvalidExpressionError):
        is_prime("7")  # type: ignore
    with pytest.raises(InvalidExpressionError):
        is_prime(3.14)  # type: ignore


def test_get_factors() -> None:
    """Test factor retrieval for positive integers."""
    assert get_factors(1) == [1]
    assert get_factors(12) == [1, 2, 3, 4, 6, 12]
    assert get_factors(28) == [1, 2, 4, 7, 14, 28]
    assert get_factors(13) == [1, 13]
    assert get_factors(36) == [1, 2, 3, 4, 6, 9, 12, 18, 36]


def test_get_factors_invalid_inputs() -> None:
    """Test get_factors rejects zero and negative values."""
    with pytest.raises(InvalidExpressionError):
        get_factors(0)
    with pytest.raises(InvalidExpressionError):
        get_factors(-10)


def test_get_prime_factors() -> None:
    """Test prime factorization with multiplicity."""
    assert get_prime_factors(12) == [2, 2, 3]
    assert get_prime_factors(60) == [2, 2, 3, 5]
    assert get_prime_factors(8) == [2, 2, 2]
    assert get_prime_factors(97) == [97]
    assert get_prime_factors(100) == [2, 2, 5, 5]


def test_get_prime_factors_invalid_inputs() -> None:
    """Test get_prime_factors rejects integers < 2."""
    with pytest.raises(InvalidExpressionError):
        get_prime_factors(1)
    with pytest.raises(InvalidExpressionError):
        get_prime_factors(0)


def test_gcd_correctness() -> None:
    """Test greatest common divisor calculations."""
    assert gcd(12, 18) == 6
    assert gcd(17, 19) == 1
    assert gcd(100, 25) == 25
    assert gcd(48, 180) == 12


def test_lcm_correctness() -> None:
    """Test least common multiple calculations."""
    assert lcm(4, 6) == 12
    assert lcm(12, 18) == 36
    assert lcm(5, 7) == 35
    assert lcm(8, 12) == 24
    assert lcm(0, 5) == 0


def test_get_multiples() -> None:
    """Test multiple generation."""
    assert get_multiples(6, 4) == [6, 12, 18, 24]
    assert get_multiples(7, 3) == [7, 14, 21]
    assert get_multiples(1, 5) == [1, 2, 3, 4, 5]

    with pytest.raises(InvalidExpressionError):
        get_multiples(-5, 3)
    with pytest.raises(InvalidExpressionError):
        get_multiples(5, 0)


def test_is_coprime() -> None:
    """Test coprime checking."""
    assert is_coprime(8, 9) is True
    assert is_coprime(14, 15) is True
    assert is_coprime(12, 18) is False
    assert is_coprime(25, 36) is True

