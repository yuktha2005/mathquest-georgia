"""Pedagogical concept explainer service for MathQuest Georgia.

Delivers structured, child-friendly explanations aligned to Georgia Standards of Excellence (MGSE).
Supports 4 distinct pedagogical styles:
- default: balanced, engaging, illustrated with relatable examples
- simpler: accessible vocabulary, visual metaphors, gentle pacing
- real_life: authentic Georgia cultural and geographic scenarios
- step_by_step: algorithmic, numbered recipe format

STRICT RULE 1 (NEVER TRUST LLM MATH):
Every single worked example has its arithmetic expression evaluated and verified
by app.services.verify.evaluate() before returning.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from app.schemas import ExplainResponse, ExplainStyle, WorkedExample
from app.services.rag import format_standards_for_prompt, retrieve_standards
from app.services.verify import evaluate, format_answer

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
RUNTIME_CACHE_DIR = DATA_DIR / "cache"
CACHE_FILE = RUNTIME_CACHE_DIR / "explanations_cache.json"
SEED_CACHE_FILE = DATA_DIR / "explanations_cache.json"


class _RawWorkedExample(BaseModel):
    problem: str
    expression: str
    steps: list[str] = Field(default_factory=list)
    claimed_answer: str = ""


class _LLMExplainSchema(BaseModel):
    title: str
    intro: str
    key_ideas: list[str]
    worked_examples: list[_RawWorkedExample]
    common_mistakes: list[str]
    standard_code: str


def _load_cache() -> dict[str, dict]:
    """Load local explanations cache from runtime cache or seed fallback."""
    target_path = CACHE_FILE if CACHE_FILE.exists() else SEED_CACHE_FILE
    if not target_path.exists():
        return {}
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Could not read explanations cache from %s: %s", target_path, exc)
        return {}


def _save_cache(cache: dict[str, dict]) -> None:
    """Save to runtime explanations cache directory."""
    try:
        RUNTIME_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as exc:
        logger.warning("Could not save to explanations cache: %s", exc)


def _get_curated_explanation(
    grade: int,
    topic: str,
    style: ExplainStyle,
    top_standard: dict,
) -> ExplainResponse:
    """Return vetted, high-quality, pre-verified explanation for offline/fallback use."""
    topic_clean = topic.lower().strip()
    std_code = top_standard.get("standard_code", f"MGSE{grade}.M")
    std_snippet = top_standard.get("summary", "")

    # Base templates by topic and grade
    if topic_clean == "fractions":
        if grade == 5:
            title = "Mastering Fractions with Unlike Denominators"
            intro = (
                "Think of fractions like sharing slices of a delicious Georgia peach pie! "
                "When bottom numbers (denominators) are different, you can't just add them up—first, "
                "cut the slices so they are the exact same size!"
                if style != ExplainStyle.SIMPLER
                else "Fractions are equal pieces of a whole pie. To add pieces with different bottoms, make them match first!"
            )
            key_ideas = [
                "The denominator (bottom number) shows how many equal parts make the whole.",
                "To add or subtract fractions with unlike denominators, find the Least Common Denominator (LCD).",
                "Multiply top and bottom by the same number to make equivalent fractions without changing their value.",
                "Once denominators match, add or subtract the numerators (tops) only, keeping the denominator identical.",
            ]
            common_mistakes = [
                "Adding both the tops AND bottoms together (e.g., thinking 1/3 + 1/4 = 2/7). Never add denominators!",
                "Forgetting to multiply the top numerator when converting to a common denominator.",
                "Leaving the final fraction unsimplified when both numbers share a common factor.",
            ]
            ex1_problem = "At the Georgia Peach Festival, Maya drinks 1/3 gallon of peach punch and Leo drinks 1/4 gallon. How much punch did they drink together?"
            ex1_expr = "1/3 + 1/4"
            ex1_steps = [
                "Step 1: Notice the denominators 3 and 4 are different.",
                "Step 2: Find the Least Common Denominator for 3 and 4, which is 12.",
                "Step 3: Convert 1/3 to 4/12 (multiply top & bottom by 4).",
                "Step 4: Convert 1/4 to 3/12 (multiply top & bottom by 3).",
                "Step 5: Add numerators: 4/12 + 3/12 = 7/12 gallon.",
            ]
            ex2_problem = "A baker in Savannah had 5/6 of a pound of pecans and used 1/6 of a pound in a praline recipe. How many pounds remain?"
            ex2_expr = "5/6 - 1/6"
            ex2_steps = [
                "Step 1: Check denominators: both fractions already have 6 as the denominator!",
                "Step 2: Subtract the numerators: 5 - 1 = 4.",
                "Step 3: Keep the denominator 6: result is 4/6.",
                "Step 4: Simplify by dividing top and bottom by 2 to get 2/3 pound.",
            ]
        else:
            title = "Dividing Fractions & Reciprocals"
            intro = (
                "Dividing fractions asks: 'How many small pieces fit inside a bigger amount?' "
                "Use the famous Keep-Change-Flip method to turn tricky division into simple multiplication!"
            )
            key_ideas = [
                "Dividing by a fraction means multiplying by its reciprocal (the upside-down fraction).",
                "Remember 'Keep-Change-Flip': Keep the 1st fraction, Change ÷ to ×, Flip the 2nd fraction.",
                "Multiply the numerators straight across, then multiply denominators straight across.",
                "Simplify your resulting fraction to simplest form or a mixed number.",
            ]
            common_mistakes = [
                "Flipping the first fraction instead of the second one.",
                "Forgetting to change the division sign to multiplication.",
                "Trying to find a common denominator for division (not needed for Keep-Change-Flip!).",
            ]
            ex1_problem = "A hiking guide on the Appalachian Trail in Georgia has 3/4 pound of trail mix and wants to pack snack bags of 1/8 pound each. How many snack bags can she make?"
            ex1_expr = "3/4 / 1/8"
            ex1_steps = [
                "Step 1: Write the division problem: 3/4 ÷ 1/8.",
                "Step 2: Keep 3/4, Change ÷ to ×, Flip 1/8 to 8/1.",
                "Step 3: Multiply across: (3 * 8) / (4 * 1) = 24 / 4.",
                "Step 4: Simplify 24 / 4 = 6 whole bags.",
            ]
            ex2_problem = "Multiply 2/5 of a field by 3/4 of fertilizer coverage."
            ex2_expr = "2/5 * 3/4"
            ex2_steps = [
                "Step 1: Multiply numerators: 2 * 3 = 6.",
                "Step 2: Multiply denominators: 5 * 4 = 20.",
                "Step 3: Result is 6/20. Simplify by dividing top and bottom by 2: 3/10.",
            ]

    elif topic_clean == "decimals":
        if grade == 5:
            title = "Adding, Subtracting & Multiplying Decimals"
            intro = (
                "Decimals are part of our base-ten number system, just like dollars and cents! "
                "The golden rule for adding and subtracting decimals is simple: line up the decimal points!"
            )
            key_ideas = [
                "Always line up decimal points vertically before adding or subtracting.",
                "Fill empty place values with placeholder zeros so columns have equal length.",
                "When multiplying decimals, count the total decimal places in both factors to place the decimal point in the product.",
            ]
            common_mistakes = [
                "Lining up numbers on the right side instead of aligning the decimal point.",
                "Forgetting placeholder zeros during subtraction (e.g., 5.0 - 2.35).",
                "Bringing down the decimal point straight down during multiplication (only do this for +/-!).",
            ]
            ex1_problem = "At the Atlanta Farmer's Market, Eli spends $3.45 on Vidalia onions and $2.80 on peaches. How much did he spend in total?"
            ex1_expr = "3.45 + 2.80"
            ex1_steps = [
                "Step 1: Line up the decimal points vertically: 3.45 + 2.80.",
                "Step 2: Add hundredths: 5 + 0 = 5.",
                "Step 3: Add tenths: 4 + 8 = 12 tenths (write 2, carry 1 to ones).",
                "Step 4: Add ones: 1 (carried) + 3 + 2 = 6.",
                "Step 5: Bring the decimal point straight down: $6.25.",
            ]
            ex2_problem = "A long jump athlete jumped 4.50 meters in their first attempt and 1.65 meters in a practice warmup. How much further was the first attempt?"
            ex2_expr = "4.50 - 1.65"
            ex2_steps = [
                "Step 1: Line up decimal points vertically: 4.50 - 1.65.",
                "Step 2: Regroup across place values: 10 - 5 = 5 in the hundredths.",
                "Step 3: 14 - 6 = 8 in the tenths.",
                "Step 4: 3 - 1 = 2 in the ones.",
                "Step 5: Result is 2.85 meters.",
            ]
        else:
            title = "Fluency with Multi-Digit Decimal Operations"
            intro = (
                "Grade 6 decimal fluency means tackling division and multiplication with confidence! "
                "In division, make the outside number (divisor) a whole number before you divide."
            )
            key_ideas = [
                "Multiply as whole numbers first, then count total decimal places to place the decimal point.",
                "In division, shift the divisor's decimal point to make it a whole number; shift the dividend identically.",
                "Estimate beforehand to make sure your decimal point placement is reasonable.",
            ]
            common_mistakes = [
                "Shifting the decimal point in the divisor but forgetting to shift it the same amount in the dividend.",
                "Miscounting total decimal places in the product when zero appears at the end (e.g., 0.2 * 0.5 = 0.10).",
            ]
            ex1_problem = "A scientist at Georgia Tech runs an experiment using 4.2 grams of catalyst per batch. If she runs 1.5 batches, how many grams are used?"
            ex1_expr = "4.2 * 1.5"
            ex1_steps = [
                "Step 1: Count decimal digits: 4.2 has 1, 1.5 has 1 (total = 2 digits).",
                "Step 2: Multiply as whole numbers: 42 * 15 = 630.",
                "Step 3: Place decimal point 2 places from the right: 6.30 = 6.3 grams.",
            ]
            ex2_problem = "Three friends split a 9.6-mile bike ride on the Atlanta BeltLine equally. How many miles does each friend ride?"
            ex2_expr = "9.6 / 3"
            ex2_steps = [
                "Step 1: The divisor 3 is already a whole number.",
                "Step 2: Divide 9 by 3 = 3.",
                "Step 3: Put decimal point in quotient.",
                "Step 4: Divide 6 by 3 = 2. Answer: 3.2 miles.",
            ]

    elif topic_clean == "ratios":
        if grade == 5:
            title = "Patterns, Scaling & Proportional Foundations"
            intro = (
                "Ratios are all about patterns and multiplication scaling! When you double or triple "
                "ingredients in a recipe, you are using the foundation of proportional thinking."
            )
            key_ideas = [
                "Multiplying a quantity by a factor greater than 1 scales it up; less than 1 scales it down.",
                "Ratio tables track pairs of numbers that grow at a consistent multiplier.",
                "Coordinate pairs (x, y) generated from rules represent proportional growth on a graph.",
            ]
            common_mistakes = [
                "Adding the same number to both terms instead of multiplying by the scale factor.",
                "Mixing up the order of numbers in a comparison.",
            ]
            ex1_problem = "A basket has a ratio of 2 red apples to 5 green apples. If we triple the batch, how many red apples do we get?"
            ex1_expr = "2 * 3"
            ex1_steps = [
                "Step 1: Identify the scale factor: tripling means multiplying by 3.",
                "Step 2: Multiply the red apples term: 2 * 3 = 6 red apples.",
            ]
            ex2_problem = "A recipe calls for 12 ounces of Georgia honey, but you only want to make 3/4 of the recipe. How many ounces should you use?"
            ex2_expr = "12 * 3/4"
            ex2_steps = [
                "Step 1: Multiply whole number by numerator: 12 * 3 = 36.",
                "Step 2: Divide by denominator: 36 / 4 = 9 ounces.",
            ]
        else:
            title = "Ratios, Unit Rates & Proportions"
            intro = (
                "A ratio compares two quantities, such as 3 cups of flour for every 2 eggs. "
                "A unit rate tells you how much for ONE single unit, like miles per hour or price per pound!"
            )
            key_ideas = [
                "Ratios can be written in 3 ways: '3 to 2', '3:2', or '3/2'.",
                "Unit rate means 'for each 1 unit': divide numerator by denominator (e.g., $6 for 4 peaches = $1.50 per peach).",
                "Equivalent ratios have equal cross-products: a/b = c/d means a*d = b*c.",
            ]
            common_mistakes = [
                "Writing the ratio terms backwards (e.g., beaks to wings vs wings to beaks).",
                "Dividing the wrong quantity when calculating unit rate (remember: dollars over items for unit price).",
            ]
            ex1_problem = "A lemonade stand uses a ratio of 3 cups of lemon juice to 2 cups of sugar. If you use 6 cups of sugar, how many cups of lemon juice do you need?"
            ex1_expr = "(3 / 2) * 6"
            ex1_steps = [
                "Step 1: Set up the proportion: 3/2 = x/6.",
                "Step 2: Find the scale factor: 6 ÷ 2 = 3.",
                "Step 3: Multiply the top by 3: 3 * 3 = 9 cups of lemon juice.",
            ]
            ex2_problem = "A roadside farm stand in Macon sells 4 Georgia peaches for $6.00. What is the unit price per peach?"
            ex2_expr = "6.00 / 4"
            ex2_steps = [
                "Step 1: Write unit price formula: Total Cost ÷ Number of Peaches.",
                "Step 2: Divide 6.00 by 4.",
                "Step 3: 6.00 / 4 = 1.50. Each peach costs $1.50.",
            ]

    elif topic_clean == "factors_multiples":
        title = "Factors, Multiples, Primes & HCF/LCM"
        intro = (
            "Numbers have secret building blocks called factors! Prime numbers are the pure building blocks "
            "that cannot be broken down further. Finding common factors (HCF) and common multiples (LCM) "
            "unlocks powerful problem-solving tricks!"
        )
        key_ideas = [
            "A factor divides evenly into a number with zero remainder (e.g., factors of 12 are 1, 2, 3, 4, 6, 12).",
            "A prime number has EXACTLY two distinct factors: 1 and itself (note: 1 is neither prime nor composite).",
            "The Highest Common Factor (HCF or GCD) is the largest factor shared by two numbers.",
            "The Lowest Common Multiple (LCM) is the smallest positive number that is a multiple of both.",
        ]
        common_mistakes = [
            "Thinking that 1 is a prime number (1 only has one factor, so it is neither prime nor composite).",
            "Confusing factors (smaller or equal) with multiples (larger or equal).",
            "Assuming all odd numbers are prime (e.g., 9, 15, and 21 are composite!).",
        ]
        ex1_problem = "Find the Lowest Common Multiple (LCM) of 4 and 6."
        ex1_expr = "12"
        ex1_steps = [
            "Step 1: List the multiples of 4: 4, 8, 12, 16, 20...",
            "Step 2: List the multiples of 6: 6, 12, 18, 24...",
            "Step 3: Identify the smallest common multiple that appears in both lists: 12.",
        ]
        ex2_problem = "A student has 18 blue beads and 24 gold beads. What is the greatest number of identical gift bags they can make without leftovers?"
        ex2_expr = "6"
        ex2_steps = [
            "Step 1: The question asks for the Highest Common Factor (HCF) of 18 and 24.",
            "Step 2: Factors of 18: 1, 2, 3, 6, 9, 18.",
            "Step 3: Factors of 24: 1, 2, 3, 4, 6, 8, 12, 24.",
            "Step 4: The greatest factor common to both lists is 6 bags.",
        ]

    elif topic_clean == "integers":
        title = "Exploring Integers & the Number Line"
        intro = (
            "Integers are whole numbers that can be positive, zero, or negative! Think of a thermometer: "
            "above zero is positive (warm), and below zero is negative (freezing). Zero is the calm center."
        )
        key_ideas = [
            "Positive integers lie to the right of zero on a number line; negative integers lie to the left.",
            "The further left a number is on the number line, the smaller it is (e.g., -5 is smaller than -2).",
            "Adding a positive number means moving right; adding a negative number means moving left.",
            "The absolute value |x| represents distance from zero and is always non-negative.",
        ]
        common_mistakes = [
            "Thinking that -10 is greater than -2 because 10 is bigger than 2 (on the negative side, -10 is further left!).",
            "Applying the multiplication rule ('two negatives make a positive') to addition (e.g., -3 + -4 = -7, NOT +7).",
        ]
        ex1_problem = "The morning temperature was -4°C in the mountains. By afternoon, it rose by 7°C. What was the afternoon temperature?"
        ex1_expr = "-4 + 7"
        ex1_steps = [
            "Step 1: Start at -4 on the number line.",
            "Step 2: Rising temperature means adding positive 7 (move 7 steps to the right).",
            "Step 3: Moving 4 steps right reaches 0, and 3 more steps reaches +3.",
            "Step 4: -4 + 7 = 3°C.",
        ]
        ex2_problem = "A submarine dives 8 meters below sea level (-8) and then descends another 5 meters (-5). What is its depth?"
        ex2_expr = "-8 - 5"
        ex2_steps = [
            "Step 1: Start at -8 meters.",
            "Step 2: Descending another 5 meters means subtracting 5 (moving further left into negative).",
            "Step 3: -8 - 5 = -13 meters.",
        ]

    else:  # geometry
        if grade == 5:
            title = "Perimeter, Area & Volume of Prisms"
            intro = (
                "Geometry lets us measure the world! Perimeter measures the fence around a shape, "
                "Area measures the carpet covering the flat floor, and Volume measures how many 3D blocks fit inside a box!"
            )
            key_ideas = [
                "Perimeter is the distance all the way around: P = 2 * (length + width).",
                "Area is 2D surface coverage: Area = length * width.",
                "Volume measures 3D space: Volume = length * width * height (or Base Area * height).",
            ]
            common_mistakes = [
                "Confusing perimeter (units) with area (square units).",
                "Forgetting to multiply all 3 dimensions when calculating volume.",
            ]
            ex1_problem = "A rectangular community garden plot in Savannah has a length of 8 feet and a width of 5 feet. What is the perimeter?"
            ex1_expr = "2 * (8 + 5)"
            ex1_steps = [
                "Step 1: Perimeter formula: P = 2 * (length + width).",
                "Step 2: Add length and width: 8 + 5 = 13 feet.",
                "Step 3: Multiply by 2: 2 * 13 = 26 feet of fencing.",
            ]
            ex2_problem = "Find the volume of a rectangular shipping crate with length 6 feet, width 4 feet, and height 3 feet."
            ex2_expr = "6 * 4 * 3"
            ex2_steps = [
                "Step 1: Volume formula: V = length * width * height.",
                "Step 2: Multiply length and width: 6 * 4 = 24 square feet (base area).",
                "Step 3: Multiply by height: 24 * 3 = 72 cubic feet.",
            ]
        else:
            title = "Area of Triangles & Polygons"
            intro = (
                "Any triangle is exactly half of a rectangle! That is why the formula for the area of a "
                "triangle is (base × height) ÷ 2. Measure the height straight up at a 90-degree right angle."
            )
            key_ideas = [
                "Triangle Area Formula: Area = (1/2) * base * height = (b * h) / 2.",
                "The height must always be perpendicular (form a square right angle) to the chosen base.",
                "Complex polygons can be decomposed into rectangles and triangles to find their total area.",
            ]
            common_mistakes = [
                "Forgetting to divide by 2 when computing triangle area.",
                "Using the slanted side of a triangle instead of the vertical perpendicular height.",
            ]
            ex1_problem = "A triangular sail on Lake Lanier has a base of 8 meters and a height of 5 meters. What is the area of the sail?"
            ex1_expr = "(8 * 5) / 2"
            ex1_steps = [
                "Step 1: Use triangle area formula: Area = (base * height) / 2.",
                "Step 2: Multiply base and height: 8 * 5 = 40.",
                "Step 3: Divide by 2: 40 / 2 = 20 square meters.",
            ]
            ex2_problem = "Find the area of a triangle with a base of 12 cm and a height of 7 cm."
            ex2_expr = "(12 * 7) / 2"
            ex2_steps = [
                "Step 1: Multiply base times height: 12 * 7 = 84.",
                "Step 2: Divide by 2: 84 / 2 = 42 square centimeters.",
            ]

    # Verify both worked examples mathematically using evaluate() (Rule 1)
    ans1_frac = evaluate(ex1_expr)
    ans2_frac = evaluate(ex2_expr)
    ans1_str = format_answer(ans1_frac, style="fraction" if ans1_frac.denominator > 1 else "decimal")
    ans2_str = format_answer(ans2_frac, style="fraction" if ans2_frac.denominator > 1 else "decimal")

    # Style modifications
    if style == ExplainStyle.SIMPLER:
        title = f"Quick & Easy Guide: {title}"
        intro = f"Here is the simple trick: {intro}"
    elif style == ExplainStyle.REAL_LIFE:
        title = f"Real-World Georgia Math: {title}"
        intro = f"How Georgians use this every day: {intro}"
    elif style == ExplainStyle.STEP_BY_STEP:
        title = f"Step-by-Step Blueprint: {title}"
        intro = f"Follow this clear recipe to solve any problem: {intro}"

    return ExplainResponse(
        title=title,
        intro=intro,
        key_ideas=key_ideas,
        worked_examples=[
            WorkedExample(
                problem=ex1_problem,
                expression=ex1_expr,
                steps=ex1_steps,
                verified_answer=ans1_str,
            ),
            WorkedExample(
                problem=ex2_problem,
                expression=ex2_expr,
                steps=ex2_steps,
                verified_answer=ans2_str,
            ),
        ],
        common_mistakes=common_mistakes,
        standard_code=std_code,
        standard_snippet=std_snippet,
        topic=topic_clean,
        grade=grade,
        style=style,
        cached=False,
    )


def get_topic_explanation(
    grade: int,
    topic: str,
    style: ExplainStyle = ExplainStyle.DEFAULT,
) -> ExplainResponse:
    """Retrieve or generate structured concept explanation with verified worked examples.

    1. Checks local cache or Supabase.
    2. If not cached, generates via Gemini if available, verifying worked examples with verify.py.
    3. Falls back safely to curated, verified explanation.
    4. Caches and returns ExplainResponse.
    """
    topic_clean = topic.lower().strip()
    cache_key = f"{grade}_{topic_clean}_{style.value}"
    local_cache = _load_cache()

    # 1. Check local cache
    if cache_key in local_cache:
        try:
            cached_item = local_cache[cache_key].copy()
            cached_item["cached"] = True
            logger.info("Serving explanation from local cache for %s", cache_key)
            return ExplainResponse.model_validate(cached_item)
        except Exception as exc:
            logger.warning("Cached entry invalid for %s: %s", cache_key, exc)

    # 2. Retrieve top 2 standards for context
    standards = retrieve_standards(query=topic_clean, topic=topic_clean, grade=grade, limit=2)
    top_standard = standards[0] if standards else {"standard_code": f"MGSE{grade}", "summary": ""}
    standards_ctx = format_standards_for_prompt(standards)

    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL")

    # 3. If Gemini is available, attempt dynamic generation
    if gemini_key and gemini_model:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            style_instruction = {
                ExplainStyle.DEFAULT: "Create a balanced, engaging explanation with clear visuals.",
                ExplainStyle.SIMPLER: "Use elementary vocabulary, visual metaphors (pies, blocks), and very gentle pacing.",
                ExplainStyle.REAL_LIFE: "Anchor problems in authentic Georgia culture, geography (Savannah, Atlanta, Okefenokee, Piedmont Park), and daily life.",
                ExplainStyle.STEP_BY_STEP: "Use a strict numbered recipe format for every concept and problem.",
            }.get(style, "Create an engaging explanation.")

            prompt = f"""You are MathQuest Georgia's expert educator.
Create a structured math lesson for Grade {grade} students on '{topic_clean}'.
Pedagogical style: {style.value.upper()} ({style_instruction}).

CURRICULUM STANDARDS (MGSE):
{standards_ctx}

REQUIREMENTS:
1. title: Engaging kid-friendly headline.
2. intro: 2-3 encouraging sentences explaining the concept.
3. key_ideas: 3-4 bullet points of core rules.
4. worked_examples: EXACTLY 2 worked examples. Each MUST have:
   - problem: Engaging word problem.
   - expression: Solvable math expression (e.g. '1/3 + 1/4' or '3.45 + 2.80').
   - steps: 3-5 clear numbered steps.
   - claimed_answer: The exact answer string.
5. common_mistakes: 2-3 typical student misconceptions.
6. standard_code: Must be {top_standard.get('standard_code', 'MGSE')}.
"""
            response = client.models.generate_content(
                model=gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=_LLMExplainSchema,
                    temperature=0.2,
                ),
            )
            raw_data = json.loads(response.text)
            parsed_schema = _LLMExplainSchema.model_validate(raw_data)

            # Strictly verify both worked examples using evaluate() (Rule 1)
            verified_examples: list[WorkedExample] = []
            for ex in parsed_schema.worked_examples[:2]:
                try:
                    ans_frac = evaluate(ex.expression)
                    ans_str = format_answer(ans_frac, style="fraction" if ans_frac.denominator > 1 else "decimal")
                    verified_examples.append(
                        WorkedExample(
                            problem=ex.problem,
                            expression=ex.expression,
                            steps=ex.steps,
                            verified_answer=ans_str,
                        )
                    )
                except Exception as eval_exc:
                    logger.warning("LLM worked example expression '%s' failed evaluation: %s", ex.expression, eval_exc)

            if len(verified_examples) == 2:
                result = ExplainResponse(
                    title=parsed_schema.title,
                    intro=parsed_schema.intro,
                    key_ideas=parsed_schema.key_ideas,
                    worked_examples=verified_examples,
                    common_mistakes=parsed_schema.common_mistakes,
                    standard_code=parsed_schema.standard_code or top_standard.get("standard_code", "MGSE"),
                    standard_snippet=top_standard.get("summary", ""),
                    topic=topic_clean,
                    grade=grade,
                    style=style,
                    cached=False,
                )
                # Save to cache
                local_cache[cache_key] = result.model_dump()
                _save_cache(local_cache)
                return result
        except Exception as exc:
            logger.warning("Dynamic Gemini explanation generation failed (%s). Using curated verified fallback.", exc)

    # 4. Fallback to curated, mathematically verified explanation
    logger.info("Using curated pre-verified explanation for %s", cache_key)
    result = _get_curated_explanation(grade, topic_clean, style, top_standard)
    local_cache[cache_key] = result.model_dump()
    _save_cache(local_cache)
    return result
