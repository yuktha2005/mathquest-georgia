"""Mathematical verification and expression evaluation service.

Enforces Rule 1: Never trust LLM math. Every single generated question
and calculation must be mathematically verified before reaching the user.

Provides safe tokenization and recursive-descent parsing without eval().
Supports integers, decimals, fractions (e.g., 3/4), mixed numbers (e.g., 2 1/3),
and standard arithmetic operations with parentheses and PEMDAS precedence.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from fractions import Fraction
import math
import re
from typing import Literal


# ============================================================================
# Exceptions
# ============================================================================

class MathVerificationError(Exception):
    """Base exception for all math parsing and verification errors."""
    pass


class DivisionByZeroError(MathVerificationError):
    """Raised when an expression attempts to divide by zero."""
    pass


class InvalidExpressionError(MathVerificationError):
    """Raised when an expression has invalid syntax or unsupported characters."""
    pass


# ============================================================================
# Token Definitions & Tokenizer
# ============================================================================

class TokenType(Enum):
    NUMBER = "NUMBER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: Fraction | None
    pos: int


# Regex pattern for mixed numbers: e.g. "2 1/3", "12 3/4"
MIXED_NUMBER_PATTERN = re.compile(r"^(\d+)\s+([0-9]\d*)\s*/\s*([0-9]\d*)(?![\d./])")
# Regex pattern for integers and decimal numbers: e.g. "2.5", ".75", "42"
NUMBER_PATTERN = re.compile(r"^(\d+\.\d+|\.\d+|\d+)(?![\d.])")


def tokenize(expression: str) -> list[Token]:
    """Safely convert an expression string into a stream of tokens.
    
    Rejects any unallowed characters (letters, underscores, quotes, etc.),
    preventing any possibility of code injection or eval exploits.
    """
    if not expression or not expression.strip():
        raise InvalidExpressionError("Expression cannot be empty.")

    tokens: list[Token] = []
    i = 0
    n = len(expression)

    while i < n:
        char = expression[i]

        # 1. Skip whitespace
        if char.isspace():
            i += 1
            continue

        # 2. Check for mixed numbers first: e.g. "2 1/3"
        mixed_match = MIXED_NUMBER_PATTERN.match(expression[i:])
        if mixed_match:
            whole = int(mixed_match.group(1))
            num = int(mixed_match.group(2))
            den = int(mixed_match.group(3))

            if den == 0:
                raise DivisionByZeroError(f"Denominator cannot be zero in mixed number at position {i}.")

            val = Fraction(whole * den + num, den)
            tokens.append(Token(TokenType.NUMBER, val, i))
            i += mixed_match.end()
            continue

        # 3. Check for decimals and plain integers: e.g. "2.5", "42"
        num_match = NUMBER_PATTERN.match(expression[i:])
        if num_match:
            num_str = num_match.group(1)
            val = Fraction(num_str)
            tokens.append(Token(TokenType.NUMBER, val, i))
            i += num_match.end()
            continue

        # 4. Check for standard and unicode arithmetic operators
        if char == "+":
            tokens.append(Token(TokenType.PLUS, None, i))
            i += 1
        elif char in ("-", "\u2212"):  # '-' or unicode minus '−'
            tokens.append(Token(TokenType.MINUS, None, i))
            i += 1
        elif char in ("*", "\u00d7"):  # '*' or unicode times '×'
            tokens.append(Token(TokenType.STAR, None, i))
            i += 1
        elif char in ("/", "\u00f7"):  # '/' or unicode divide '÷'
            tokens.append(Token(TokenType.SLASH, None, i))
            i += 1
        elif char == "(":
            tokens.append(Token(TokenType.LPAREN, None, i))
            i += 1
        elif char == ")":
            tokens.append(Token(TokenType.RPAREN, None, i))
            i += 1
        else:
            raise InvalidExpressionError(
                f"Unexpected character '{char}' at position {i}. Only numbers, math operators (+, -, *, /), and parentheses are permitted."
            )

    tokens.append(Token(TokenType.EOF, None, n))
    return tokens


# ============================================================================
# Recursive Descent Parser
# ============================================================================

class Parser:
    """Safe recursive-descent mathematical parser.

    Grammar:
        expression := term (( '+' | '-' ) term)*
        term       := factor (( '*' | '/' ) factor)*
        factor     := ('+' | '-') factor | primary
        primary    := NUMBER | '(' expression ')'
    """

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current_index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.current_index]

    def consume(self, expected_type: TokenType | None = None) -> Token:
        token = self.current
        if expected_type and token.type != expected_type:
            raise InvalidExpressionError(
                f"Expected token {expected_type.value} at position {token.pos}, found {token.type.value}."
            )
        self.current_index += 1
        return token

    def parse(self) -> Fraction:
        if self.current.type == TokenType.EOF:
            raise InvalidExpressionError("Expression cannot be empty.")
        result = self.expression()
        if self.current.type != TokenType.EOF:
            raise InvalidExpressionError(
                f"Unexpected token '{self.current.type.value}' at position {self.current.pos}."
            )
        return result

    def expression(self) -> Fraction:
        """Parse addition and subtraction (lowest precedence)."""
        result = self.term()

        while self.current.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.consume().type
            right = self.term()
            if op == TokenType.PLUS:
                result = result + right
            else:
                result = result - right

        return result

    def term(self) -> Fraction:
        """Parse multiplication and division (medium precedence)."""
        result = self.factor()

        while self.current.type in (TokenType.STAR, TokenType.SLASH):
            op = self.consume().type
            right = self.factor()
            if op == TokenType.STAR:
                result = result * right
            else:
                if right == 0:
                    raise DivisionByZeroError("Division by zero encountered in expression.")
                result = result / right

        return result

    def factor(self) -> Fraction:
        """Parse unary operators (+, -) and primaries."""
        if self.current.type == TokenType.PLUS:
            self.consume(TokenType.PLUS)
            return self.factor()
        elif self.current.type == TokenType.MINUS:
            self.consume(TokenType.MINUS)
            return -self.factor()
        return self.primary()

    def primary(self) -> Fraction:
        """Parse numeric literals and parenthesized expressions."""
        token = self.current

        if token.type == TokenType.NUMBER:
            self.consume(TokenType.NUMBER)
            assert token.value is not None
            return token.value

        if token.type == TokenType.LPAREN:
            lparen_pos = token.pos
            self.consume(TokenType.LPAREN)

            if self.current.type == TokenType.RPAREN:
                raise InvalidExpressionError(
                    f"Empty parentheses '()' at position {lparen_pos} are not allowed."
                )

            val = self.expression()

            if self.current.type != TokenType.RPAREN:
                raise InvalidExpressionError(
                    f"Unclosed parenthesis: expected ')' for '(' at position {lparen_pos}."
                )
            self.consume(TokenType.RPAREN)
            return val

        if token.type == TokenType.EOF:
            raise InvalidExpressionError("Unexpected end of expression after operator.")

        raise InvalidExpressionError(
            f"Unexpected token '{token.type.value}' at position {token.pos}."
        )


# ============================================================================
# Public API
# ============================================================================

class AnswerStyle(str, Enum):
    """Output formatting styles for verified mathematical results."""
    FRACTION = "fraction"
    MIXED = "mixed"
    DECIMAL = "decimal"


def evaluate(expression: str) -> Fraction:
    """Safely parse and evaluate an arithmetic expression into an exact Fraction.

    Supports:
        - Integers, decimals (e.g. 2.5), fractions (e.g. 3/4), and mixed numbers (e.g. "2 1/3")
        - Operators: +, -, *, / (and unicode equivalents −, ×, ÷)
        - Arbitrarily nested parentheses
        - Strict validation rejecting malicious code or unallowed characters

    Raises:
        DivisionByZeroError: If division by zero occurs anywhere in the expression.
        InvalidExpressionError: If syntax is invalid, empty, or unallowed characters exist.
    """
    tokens = tokenize(expression)
    parser = Parser(tokens)
    return parser.parse()


def format_answer(
    value: Fraction,
    style: AnswerStyle | Literal["fraction", "mixed", "decimal"] | str = AnswerStyle.FRACTION,
    decimal_places: int = 4,
) -> str:
    """Format an exact Fraction as a simplified fraction, mixed number, or decimal.

    Args:
        value: The Fraction to format.
        style: "fraction" (or AnswerStyle.FRACTION), "mixed", or "decimal".
        decimal_places: Maximum decimal places for non-terminating decimals (default 4).

    Returns:
        Formatted string representation.
    """
    style_str = style.value if isinstance(style, AnswerStyle) else str(style).lower().strip()

    # 1. Simplified Fraction style: e.g. "3/4", "5/2", "3"
    if style_str in ("fraction", "simplified_fraction", "simple"):
        if value.denominator == 1:
            return str(value.numerator)
        return f"{value.numerator}/{value.denominator}"

    # 2. Mixed Number style: e.g. "2 1/3", "3/4", "5", "-2 1/3"
    if style_str in ("mixed", "mixed_number"):
        num = value.numerator
        den = value.denominator

        if den == 1:
            return str(num)

        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        whole = abs_num // den
        remainder = abs_num % den

        if whole == 0:
            return f"{sign}{remainder}/{den}"
        return f"{sign}{whole} {remainder}/{den}"

    # 3. Decimal style: e.g. "0.75", "2.5", "2.3333"
    if style_str in ("decimal", "float"):
        # Check if fraction terminates (denominator prime factors only 2 and 5)
        temp_d = abs(value.denominator)
        while temp_d % 2 == 0:
            temp_d //= 2
        while temp_d % 5 == 0:
            temp_d //= 5

        if temp_d == 1:
            # Terminating decimal: exact representation
            dec = Decimal(value.numerator) / Decimal(value.denominator)
            if dec == dec.to_integral():
                return str(int(dec))
            s = f"{dec:f}"
            if "." in s:
                s = s.rstrip("0").rstrip(".")
            return s
        else:
            # Repeating/non-terminating decimal: format to specified decimal places
            val_float = float(value)
            formatted = f"{val_float:.{decimal_places}f}".rstrip("0").rstrip(".")
            return formatted

    raise ValueError(
        f"Unsupported answer style '{style}'. Permitted styles are 'fraction', 'mixed', or 'decimal'."
    )


def verify_math_expression(expression: str) -> bool:
    """Helper verifying if an expression is mathematically valid and solvable."""
    try:
        evaluate(expression)
        return True
    except MathVerificationError:
        return False


# ============================================================================
# Deterministic Geometry Verification Helpers
# ============================================================================

def _to_fraction(val: int | float | str | Fraction, name: str = "dimension") -> Fraction:
    """Safely convert numeric dimension inputs to positive exact Fraction."""
    if isinstance(val, Fraction):
        res = val
    elif isinstance(val, (int, str)):
        try:
            res = Fraction(str(val).strip())
        except (ValueError, ZeroDivisionError) as e:
            raise InvalidExpressionError(f"Invalid numeric input for {name}: '{val}'") from e
    elif isinstance(val, float):
        res = Fraction(Decimal(str(val)))
    else:
        raise InvalidExpressionError(f"Unsupported type {type(val)} for {name}")

    if res <= 0:
        raise InvalidExpressionError(f"{name.capitalize()} must be strictly positive, got {val}")
    return res


def rectangle_area(
    length: int | float | str | Fraction,
    width: int | float | str | Fraction,
) -> Fraction:
    """Calculate exact area of a rectangle: length * width."""
    return _to_fraction(length, "length") * _to_fraction(width, "width")


def rectangle_perimeter(
    length: int | float | str | Fraction,
    width: int | float | str | Fraction,
) -> Fraction:
    """Calculate exact perimeter of a rectangle: 2 * (length + width)."""
    return Fraction(2, 1) * (_to_fraction(length, "length") + _to_fraction(width, "width"))


def square_area(side: int | float | str | Fraction) -> Fraction:
    """Calculate exact area of a square: side * side."""
    s = _to_fraction(side, "side")
    return s * s


def square_perimeter(side: int | float | str | Fraction) -> Fraction:
    """Calculate exact perimeter of a square: 4 * side."""
    return Fraction(4, 1) * _to_fraction(side, "side")


def triangle_area(
    base: int | float | str | Fraction,
    height: int | float | str | Fraction,
) -> Fraction:
    """Calculate exact area of a triangle: 1/2 * base * height."""
    return Fraction(1, 2) * _to_fraction(base, "base") * _to_fraction(height, "height")


def triangle_perimeter(
    side_a: int | float | str | Fraction,
    side_b: int | float | str | Fraction,
    side_c: int | float | str | Fraction,
) -> Fraction:
    """Calculate exact perimeter of a triangle: a + b + c."""
    return (
        _to_fraction(side_a, "side_a")
        + _to_fraction(side_b, "side_b")
        + _to_fraction(side_c, "side_c")
    )


def parallelogram_area(
    base: int | float | str | Fraction,
    height: int | float | str | Fraction,
) -> Fraction:
    """Calculate exact area of a parallelogram: base * height."""
    return _to_fraction(base, "base") * _to_fraction(height, "height")


def parallelogram_perimeter(
    base: int | float | str | Fraction,
    side: int | float | str | Fraction,
) -> Fraction:
    """Calculate exact perimeter of a parallelogram: 2 * (base + side)."""
    return Fraction(2, 1) * (_to_fraction(base, "base") + _to_fraction(side, "side"))


# ============================================================================
# Deterministic Number Theory Helpers (CBSE Class 6 Ganita Prakash)
# ============================================================================

def is_prime(n: int) -> bool:
    """Check if an integer n is prime.

    Primes are integers greater than 1 with no positive divisors other than 1 and itself.
    """
    if not isinstance(n, int):
        raise InvalidExpressionError(f"Expected integer for primality check, got {type(n)}")
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def get_factors(n: int) -> list[int]:
    """Return all positive factors (divisors) of n in ascending sorted order."""
    if not isinstance(n, int) or n < 1:
        raise InvalidExpressionError(f"Factors require a positive integer (>= 1), got {n}")
    factors: set[int] = set()
    limit = math.isqrt(n)
    for i in range(1, limit + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(factors)


def get_prime_factors(n: int) -> list[int]:
    """Return the prime factorization of n as a list of prime factors with multiplicity."""
    if not isinstance(n, int) or n < 2:
        raise InvalidExpressionError(f"Prime factorization requires an integer >= 2, got {n}")
    factors: list[int] = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1 if d == 2 else 2
    if temp > 1:
        factors.append(temp)
    return factors


def gcd(a: int, b: int) -> int:
    """Calculate the Greatest Common Divisor (GCD / HCF) of two integers."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise InvalidExpressionError(f"GCD requires integer arguments, got {type(a)} and {type(b)}")
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """Calculate the Least Common Multiple (LCM) of two integers."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise InvalidExpressionError(f"LCM requires integer arguments, got {type(a)} and {type(b)}")
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)


def get_multiples(n: int, count: int = 5) -> list[int]:
    """Return the first `count` positive multiples of n."""
    if not isinstance(n, int) or n <= 0:
        raise InvalidExpressionError(f"Multiples require a positive integer, got {n}")
    if count <= 0:
        raise InvalidExpressionError(f"Count of multiples must be positive, got {count}")
    return [n * i for i in range(1, count + 1)]


def is_coprime(a: int, b: int) -> bool:
    """Return True if a and b are coprime (share no common factors other than 1)."""
    return gcd(a, b) == 1


def verify_options_distinct(
    options: list[Any],
    claimed_answer: str | Fraction | None = None,
) -> tuple[bool, str]:
    """Verify that all multiple-choice options evaluate to pairwise-distinct Fraction values.

    Also checks that if claimed_answer is provided, exactly one option matches its Fraction value.
    """
    if len(options) < 2:
        return False, f"At least 2 options required, got {len(options)}"

    parsed_values: dict[Fraction, str] = {}
    matches_target = 0
    target_frac = evaluate(str(claimed_answer)) if claimed_answer is not None else None

    for opt in options:
        opt_text = opt.text if hasattr(opt, "text") else (opt["text"] if isinstance(opt, dict) else str(opt))
        try:
            val = evaluate(opt_text)
        except Exception as exc:
            return False, f"Option text '{opt_text}' failed evaluation: {exc}"

        if val in parsed_values:
            return False, f"Duplicate option value: '{opt_text}' has the same Fraction value ({val}) as '{parsed_values[val]}'"
        parsed_values[val] = opt_text

        if target_frac is not None and val == target_frac:
            matches_target += 1

    if target_frac is not None and matches_target != 1:
        return False, f"Expected exactly 1 option to match claimed answer {target_frac}, found {matches_target}"

    return True, "Options are pairwise distinct and valid"


def verify_stem_expression_consistency(stem: str, expression: str) -> tuple[bool, str]:
    """Verify that expression operands appear in the stem and operation matches narrative context."""
    stem_lower = stem.lower()

    # 1. Check numbers/operands
    expr_numbers = re.findall(r"\b\d+(?:/\d+|\.\d+)?\b", expression)
    formula_constants = {"0", "1", "2", "3", "4"}

    for num in expr_numbers:
        if num in stem:
            continue
        if num in formula_constants:
            continue
        try:
            f = Fraction(num)
            if f.denominator > 1 and abs(f.numerator) > f.denominator:
                whole = abs(f.numerator) // f.denominator
                rem = abs(f.numerator) % f.denominator
                mixed = f"{whole} {rem}/{f.denominator}"
                if mixed in stem:
                    continue
        except Exception:
            pass
        if "." in num and num.rstrip("0").rstrip(".") in stem:
            continue

        return False, f"Operand '{num}' from expression '{expression}' not found in stem: '{stem}'"

    # 2. Check operation words
    if "+" in expression:
        keywords = [
            "total", "together", "sum", "add", "plus", "in all", "combined",
            "both", "and", "increase", "more", "mixture", "perimeter", "grew",
            "rose", "rise", "simplify", "evaluate", "calculate", "expression"
        ]
        if not any(k in stem_lower for k in keywords):
            return False, f"Expression has '+' but stem lacks addition keywords: '{stem}'"

    # Only treat '-' as subtraction if preceded by operand (binary minus)
    if re.search(r"[\d\)]\s*-\s*[\d\(]", expression):
        keywords = [
            "left", "remain", "difference", "less", "minus", "subtract", "more than",
            "decrease", "drop", "change", "grew from", "take", "used", "shorter",
            "taller", "heavier", "lighter", "colder", "warmer", "below", "debt",
            "how many more", "simplify", "evaluate", "calculate", "expression", "hcf", "gcd"
        ]
        if not any(k in stem_lower for k in keywords):
            return False, f"Expression has '-' but stem lacks subtraction keywords: '{stem}'"

    if "*" in expression:
        keywords = [
            "each", "times", "product", "of", "area", "multipl", "every", "rate",
            "scale", "perimeter", "ratio", "lcm", "hcf", "gcd", "simplify", "evaluate", "calculate", "expression"
        ]
        if not any(k in stem_lower for k in keywords):
            return False, f"Expression has '*' but stem lacks multiplication keywords: '{stem}'"

    return True, "Consistent"


