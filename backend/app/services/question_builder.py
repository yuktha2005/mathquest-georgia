"""Question builder service implementing verification and distractor generation.

Orchestrates the question lifecycle:
1. Prompts LLM for QuestionTemplate using eval/prompts/v1.txt.
2. Validates schema with Pydantic; retries up to 2 times with a repair prompt on failure.
3. Computes the exact true answer with verify.evaluate(expression) (Rule 1).
4. Generates deterministic distractors with misconceptions.py (Rule 3) and shuffles options.
5. Falls back to data/fallback_bank.json if retries are exhausted or verification fails (Rule 2).
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
import json
import logging
from pathlib import Path
import random
import re
import time
import uuid

from app.schemas import Option, Question, QuestionTemplate, QuestionType, Tier
from app.services.curriculum import curriculum_service
from app.services.llm import generate_question_template
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
from app.services.verify import (
    MathVerificationError,
    evaluate,
    format_answer,
)

logger = logging.getLogger(__name__)

# Paths
PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "eval" / "prompts"
PROMPT_V1_PATH = PROMPTS_DIR / "v1.txt"
FALLBACK_BANK_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "fallback_bank.json"

_QUESTION_CACHE: dict[str, Question] = {}


def register_question(question: Question) -> Question:
    """Store question in memory cache for submission retrieval."""
    _QUESTION_CACHE[question.id] = question
    return question


def get_question_by_id(question_id: str) -> Question | None:
    """Retrieve question by ID from active memory cache or fallback bank."""
    if question_id in _QUESTION_CACHE:
        return _QUESTION_CACHE[question_id]

    try:
        bank = load_fallback_bank()
        for item in bank:
            raw_id = item.get("id", "")
            if raw_id == question_id or (raw_id and question_id.startswith(raw_id)):
                q = Question.model_validate(item)
                _QUESTION_CACHE[question_id] = q
                return q
    except Exception as exc:
        logger.warning("Failed to lookup question by id '%s': %s", question_id, exc)

    return None


def load_prompt_template() -> str:
    """Load system prompt template from file."""
    if not PROMPT_V1_PATH.exists():
        raise FileNotFoundError(f"Prompt file not found at {PROMPT_V1_PATH}")
    return PROMPT_V1_PATH.read_text(encoding="utf-8")


def load_fallback_bank() -> list[dict]:
    """Load the vetted offline question bank."""
    if not FALLBACK_BANK_PATH.exists():
        raise FileNotFoundError(f"Fallback bank not found at {FALLBACK_BANK_PATH}")
    with open(FALLBACK_BANK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)



def get_fallback_question(
    grade: int,
    topic: str,
    tier: Tier | str,
) -> Question:
    """Return a verified question from data/fallback_bank.json matching topic and tier."""
    items = load_fallback_bank()
    tier_str = tier.value if isinstance(tier, Tier) else str(tier).lower()
    topic_str = topic.lower()

    # Filter by topic and tier
    matching = [
        item for item in items
        if item.get("topic", "").lower() == topic_str and item.get("tier", "").lower() == tier_str
    ]

    # If no exact match, filter by topic only
    if not matching:
        matching = [item for item in items if item.get("topic", "").lower() == topic_str]

    # If still none, use entire bank
    pool = matching if matching else items
    chosen_dict = random.choice(pool).copy()

    # Assign a unique session ID while retaining question integrity
    chosen_dict["id"] = f"{chosen_dict['id']}-{uuid.uuid4().hex[:6]}"
    q = Question.model_validate(chosen_dict)
    return register_question(q)


def _generate_distractors_for_template(
    template: QuestionTemplate,
    true_val: Fraction,
) -> list[MisconceptionDistractor]:
    """Inspect question_type and operands to invoke the appropriate misconception generator."""
    true_str = format_answer(true_val, style="fraction" if true_val.denominator > 1 else "decimal")
    q_type = template.question_type
    operands = template.operands
    expression = template.expression

    # 1. Fraction Add/Sub
    if q_type == QuestionType.FRACTION_ADD_SUB or template.topic.lower() == "fractions" and ("+" in expression or "-" in expression):
        if len(operands) >= 2:
            try:
                s1, s2 = operands[0], operands[1]
                f1, f2 = evaluate(s1), evaluate(s2)
                raw = None
                if "/" in s1 and "/" in s2:
                    a, b = map(int, s1.split("/"))
                    c, d = map(int, s2.split("/"))
                    raw = (a, b, c, d)
                op = "-" if "-" in expression else "+"
                return get_fraction_add_sub_distractors(f1, f2, op, raw_operands=raw)
            except Exception:
                pass

        # Regex fallback
        add_sub_match = re.search(r"(\d+/\d+|\d+)\s*([+\-])\s*(\d+/\d+|\d+)", expression)
        if add_sub_match:
            s1, op, s2 = add_sub_match.groups()
            f1, f2 = Fraction(s1), Fraction(s2)
            raw = None
            if "/" in s1 and "/" in s2:
                a, b = map(int, s1.split("/"))
                c, d = map(int, s2.split("/"))
                raw = (a, b, c, d)
            return get_fraction_add_sub_distractors(f1, f2, op, raw_operands=raw)
        return get_fraction_add_sub_distractors(true_val, Fraction(1, 2), "+")

    # 2. Fraction Multiply/Divide
    elif q_type == QuestionType.FRACTION_MUL_DIV or template.topic.lower() == "fractions":
        if len(operands) >= 2:
            try:
                f1, f2 = evaluate(operands[0]), evaluate(operands[1])
                op = "/" if ("/" in expression or "÷" in expression) else "*"
                if op == "/" and f2 == 0:
                    f2 = Fraction(1, 2)
                return get_fraction_mult_div_distractors(f1, f2, op)
            except Exception:
                pass

        mult_div_match = re.search(r"(\d+/\d+|\d+)\s*([*/÷×])\s*(\d+/\d+|\d+)", expression)
        if mult_div_match:
            s1, op_char, s2 = mult_div_match.groups()
            op = "/" if op_char in ("/", "÷") else "*"
            f1, f2 = Fraction(s1), Fraction(s2)
            if op == "/" and f2 == 0:
                f2 = Fraction(1, 2)
            return get_fraction_mult_div_distractors(f1, f2, op)
        return get_fraction_mult_div_distractors(true_val, Fraction(2, 3), "*")

    # 3. Decimal Operations
    elif q_type == QuestionType.DECIMAL_OPS or template.topic.lower() == "decimals":
        if len(operands) >= 2:
            try:
                d1, d2 = Decimal(operands[0]), Decimal(operands[1])
                op = "-" if "-" in expression else ("*" if "*" in expression or "×" in expression else "+")
                return get_decimal_distractors(d1, d2, op, true_str)
            except Exception:
                pass

        dec_match = re.search(r"([\d.]+)\s*([+\-*])\s*([\d.]+)", expression)
        if dec_match:
            s1, op, s2 = dec_match.groups()
            try:
                return get_decimal_distractors(Decimal(s1), Decimal(s2), op, true_str)
            except Exception:
                pass
        return get_decimal_distractors(Decimal("1.5"), Decimal("0.5"), "+", true_str)

    # 4. Ratios
    elif q_type == QuestionType.RATIO or template.topic.lower() == "ratios":
        if len(operands) >= 2:
            try:
                a, b = int(float(operands[0])), int(float(operands[1]))
                target_a = int(float(operands[2])) if len(operands) >= 3 else None
                return get_ratio_distractors(a=a, b=b, target_a=target_a)
            except Exception:
                pass

        nums = [int(n) for n in re.findall(r"\b\d+\b", expression)]
        if len(nums) >= 2:
            return get_ratio_distractors(a=nums[0], b=nums[1], target_a=nums[0] * 2)
        return get_ratio_distractors(a=2, b=3, target_a=6)

    # 5. Geometry Area / Perimeter
    elif q_type == QuestionType.GEOMETRY_AREA_PERIMETER or template.topic.lower() == "geometry":
        stem_lower = template.stem.lower()
        if "parallelogram" in stem_lower:
            shape = "parallelogram"
        elif "square" in stem_lower:
            shape = "square"
        elif "triangle" in stem_lower or "/ 2" in expression or "1/2" in expression:
            shape = "triangle"
        else:
            shape = "rectangle"

        metric = "perimeter" if "perimeter" in stem_lower else "area"
        if len(operands) >= 2:
            try:
                dim1, dim2 = float(operands[0]), float(operands[1])
                return get_geometry_distractors(shape, dim1, dim2, metric)
            except Exception:
                pass
        elif len(operands) == 1 and shape == "square":
            try:
                dim1 = float(operands[0])
                return get_geometry_distractors(shape, dim1, dim1, metric)
            except Exception:
                pass

        nums = [float(n) for n in re.findall(r"\b[\d.]+\b", expression)]
        if len(nums) >= 2:
            return get_geometry_distractors(shape, nums[0], nums[1], metric)
        elif len(nums) == 1 and shape == "square":
            return get_geometry_distractors(shape, nums[0], nums[0], metric)
        return get_geometry_distractors("rectangle", 5.0, 4.0, "area")

    # 6. Factors and Multiples (CBSE)
    elif q_type == QuestionType.FACTORS_MULTIPLES or template.topic.lower() == "factors_multiples":
        target_type = "prime_factors" if "prime" in template.stem.lower() else ("multiples" if "multiple" in template.stem.lower() else "factors")
        n_val = 12
        if operands:
            try:
                n_val = int(operands[0])
            except Exception:
                pass
        else:
            found_nums = [int(n) for n in re.findall(r"\b\d+\b", expression)]
            if found_nums:
                n_val = found_nums[0]
        return get_factors_multiples_distractors(n=n_val, correct_answer=true_str, target_type=target_type)

    # 7. LCM and GCD / HCF (CBSE)
    elif q_type == QuestionType.LCM_GCD or "lcm" in template.stem.lower() or "gcd" in template.stem.lower() or "hcf" in template.stem.lower():
        target_type = "lcm" if "lcm" in template.stem.lower() or "lcm" in expression.lower() else "gcd"
        nums = [int(n) for n in re.findall(r"\b\d+\b", expression)]
        if len(nums) >= 2:
            return get_lcm_gcd_distractors(a=nums[0], b=nums[1], target_type=target_type)
        return get_lcm_gcd_distractors(a=12, b=18, target_type=target_type)

    return get_fraction_add_sub_distractors(true_val, Fraction(1, 2), "+")


def build_explanation(expression: str, true_val: Fraction) -> str:
    """Generate child-appropriate step-by-step solution walkthrough."""
    ans_style = "mixed" if true_val.denominator > 1 and abs(true_val.numerator) > true_val.denominator else "fraction"
    ans_str = format_answer(true_val, style=ans_style)
    return (
        f"Step 1: Write down the problem expression: {expression}.\n"
        f"Step 2: Solve step-by-step following the order of operations.\n"
        f"Step 3: Simplify the result to get {ans_str}.\n"
        f"Great job practicing your math skills!"
    )


def build_question_pipeline(
    grade: int,
    topic: str,
    tier: Tier | str,
    board: str = "georgia",
    llm_func=generate_question_template,
) -> tuple[Question, int, float, bool]:
    """Execute the full question building pipeline with repair retries and fallback.

    Returns:
        tuple: (Question, retries_used, latency_ms, used_fallback)
    """
    start_time = time.perf_counter()
    tier_obj = tier if isinstance(tier, Tier) else Tier(str(tier).lower())
    from app.services.rag import format_standards_for_prompt, retrieve_standards

    # Look up curriculum pack topic config for standard alignment
    topic_cfg = curriculum_service.get_topic_config(board, grade, topic)
    fallback_standard = topic_cfg.standard_code if topic_cfg else (f"MGSE{grade}.NF.1" if topic == "fractions" else f"MGSE{grade}.OA.1")

    prompt_template = load_prompt_template()
    standards = retrieve_standards(query=topic, topic=topic, grade=grade, limit=2)
    standards_ctx = format_standards_for_prompt(standards)

    base_prompt = prompt_template.format(
        grade=grade,
        topic=topic,
        tier=tier_obj.value,
        standards_context=standards_ctx,
    )

    current_prompt = base_prompt
    retries = 0
    max_retries = 2
    template: QuestionTemplate | None = None

    # Step 1 & 2: Prompt LLM and validate with up to 2 repair retries
    for attempt in range(max_retries + 1):
        try:
            template = llm_func(current_prompt)
            # Step 3: Verify the mathematical expression (Rule 1)
            true_val = evaluate(template.expression)

            # Compare claimed_answer to verified evaluation using exact Fraction equality
            if template.claimed_answer and template.claimed_answer.strip():
                claimed_val = evaluate(template.claimed_answer)
                if true_val != claimed_val:
                    raise MathVerificationError(
                        f"Claimed answer '{template.claimed_answer}' ({claimed_val}) "
                        f"does not match evaluated expression '{template.expression}' ({true_val})."
                    )
            break
        except (MathVerificationError, Exception) as exc:
            logger.warning(
                "Attempt %d/%d failed with error: %s",
                attempt + 1,
                max_retries + 1,
                exc,
            )
            retries = attempt + 1
            if attempt < max_retries:
                # Construct repair prompt with exact error context
                current_prompt = (
                    f"{base_prompt}\n\n"
                    f"PREVIOUS ATTEMPT FAILED WITH ERROR: {exc}\n"
                    f"Please repair the output. Ensure the 'expression' is solvable, child-appropriate, "
                    f"'claimed_answer' exactly equals the expression, "
                    f"and returns valid JSON matching the QuestionTemplate schema."
                )
            else:
                template = None

    # Step 5: Fall back if all retries failed or math evaluation failed
    if template is None:
        logger.warning(
            "All %d attempts failed. Falling back to data/fallback_bank.json.",
            max_retries + 1,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        fallback_q = get_fallback_question(grade, topic, tier_obj)
        if fallback_q.board != board or fallback_q.grade != grade:
            fallback_q = Question(
                id=fallback_q.id,
                board=board,
                topic=fallback_q.topic,
                grade=grade,
                tier=fallback_q.tier,
                stem=fallback_q.stem,
                expression=fallback_q.expression,
                options=fallback_q.options,
                correct_option_id=fallback_q.correct_option_id,
                explanation=fallback_q.explanation,
                standard_code=fallback_standard,
            )
        return fallback_q, max_retries, elapsed_ms, True

    # Step 4: Build Options and Distractors (Rule 3)
    try:
        true_val = evaluate(template.expression)
        true_str = format_answer(true_val, style="fraction" if true_val.denominator > 1 else "decimal")
        distractors = _generate_distractors_for_template(template, true_val)

        # Assemble the 4 choices: 1 correct + 3 distractors
        choices: list[dict] = [
            {"text": true_str, "misconception_tag": None, "is_correct": True}
        ]
        for d in distractors[:3]:
            choices.append(
                {"text": d.text, "misconception_tag": d.misconception_tag, "is_correct": False}
            )

        random.shuffle(choices)

        options: list[Option] = []
        correct_option_id = "A"
        letters = ["A", "B", "C", "D"]

        for idx, ch in enumerate(choices):
            letter = letters[idx]
            options.append(
                Option(
                    id=letter,
                    text=ch["text"],
                    misconception_tag=ch["misconception_tag"],
                )
            )
            if ch["is_correct"]:
                correct_option_id = letter

        explanation = build_explanation(template.expression, true_val)
        question_id = f"gen-{uuid.uuid4().hex[:8]}"

        question = Question(
            id=question_id,
            board=board,
            topic=template.topic,
            grade=grade,
            tier=template.tier,
            stem=template.stem,
            expression=template.expression,
            options=options,
            correct_option_id=correct_option_id,
            explanation=explanation,
            standard_code=template.standard_code or fallback_standard,
        )
        register_question(question)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return question, retries, elapsed_ms, False

    except Exception as exc:
        logger.error("Option generation failed: %s. Using fallback.", exc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        fallback_q = get_fallback_question(grade, topic, tier_obj)
        if fallback_q.board != board or fallback_q.grade != grade:
            fallback_q = Question(
                id=fallback_q.id,
                board=board,
                topic=fallback_q.topic,
                grade=grade,
                tier=fallback_q.tier,
                stem=fallback_q.stem,
                expression=fallback_q.expression,
                options=fallback_q.options,
                correct_option_id=fallback_q.correct_option_id,
                explanation=fallback_q.explanation,
                standard_code=fallback_standard,
            )
        return fallback_q, max_retries, elapsed_ms, True


def build_questions_batch(
    grade: int,
    topic: str,
    tier: Tier | str,
    count: int = 10,
    board: str = "georgia",
    llm_func=generate_question_template,
) -> tuple[list[Question], int, float]:
    """Generate a batch of verified questions (e.g. 10 for a full round).

    Applies the same verification, repair retry, and fallback safety per question.
    """
    start_time = time.perf_counter()
    questions: list[Question] = []
    total_retries = 0

    for _ in range(count):
        q, retries, _, _ = build_question_pipeline(
            grade=grade,
            topic=topic,
            tier=tier,
            board=board,
            llm_func=llm_func,
        )
        questions.append(q)
        total_retries += retries

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return questions, total_retries, elapsed_ms

