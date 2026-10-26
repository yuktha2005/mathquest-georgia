"""Service for generating and caching 6-slide pedagogical video scripts.

Produces structured 6-slide scripts for elementary topics:
- Slide 1: Welcome & Real-World Hook
- Slide 2: Core Concept Definition
- Slide 3: Visual Model Exploration
- Slide 4: Worked Example Step-by-Step
- Slide 5: Common Trap & How to Avoid It
- Slide 6: Quest Ready & Victory Cheer

Enforces Pydantic schema validation (Slide, ScriptResponse) and local caching.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from app.schemas import ScriptResponse, Slide
from app.services.rag import retrieve_standards

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
RUNTIME_CACHE_DIR = DATA_DIR / "cache"
CACHE_FILE = RUNTIME_CACHE_DIR / "scripts_cache.json"
SEED_CACHE_FILE = DATA_DIR / "scripts_cache.json"


class _LLMSlide(BaseModel):
    slide_number: int
    title: str
    bullets: list[str] = Field(default_factory=list)
    narration: str
    visual_component: str = "TopicGraphic"
    visual_props: dict[str, Any] = Field(default_factory=dict)
    duration_seconds: int = 8


class _LLMScriptSchema(BaseModel):
    title: str
    standard_code: str
    slides: list[_LLMSlide]


def _load_cache() -> dict[str, dict]:
    """Load cached video scripts from runtime cache or seed fallback."""
    target_path = CACHE_FILE if CACHE_FILE.exists() else SEED_CACHE_FILE
    if not target_path.exists():
        return {}
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Could not read scripts cache from %s: %s", target_path, exc)
        return {}


def _save_cache(cache: dict[str, dict]) -> None:
    """Save to runtime scripts cache directory."""
    try:
        RUNTIME_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as exc:
        logger.warning("Could not save to scripts cache: %s", exc)


def _get_curated_script(grade: int, topic: str, standard_code: str) -> ScriptResponse:
    """Return hand-crafted, mathematically verified 6-slide script for offline/fallback use."""
    topic_clean = topic.lower().strip()

    if topic_clean == "fractions":
        if grade == 5:
            slides = [
                Slide(
                    slide_number=1,
                    title="Welcome to Fractions Kingdom!",
                    bullets=[
                        "Sharing sweet Georgia treats in Macon",
                        "When fractions have different denominators",
                        "Our quest: Master unlike denominators!",
                    ],
                    narration="Welcome, math explorer! Imagine you and a friend are sharing delicious Georgia peach pies. Maya has one third of a pie, and Leo has one fourth. How much pie do they have together? Let's find out!",
                    visual_component="TopicGraphic",
                    visual_props={"emoji": "🍕", "label": "Peach Pie Sharing"},
                    duration_seconds=8,
                ),
                Slide(
                    slide_number=2,
                    title="The Golden Rule: Like Denominators",
                    bullets=[
                        "Denominator tells the total equal slices in a whole",
                        "You CANNOT add slices of different sizes",
                        "Find a Common Denominator before adding",
                    ],
                    narration="Here is the golden rule of fractions: the denominator tells us how many equal pieces make up the whole pie. If the bottom numbers are different, the slices are different sizes! We must cut them so they match.",
                    visual_component="FractionBar",
                    visual_props={"numerator": 1, "denominator": 3},
                    duration_seconds=8,
                ),
                Slide(
                    slide_number=3,
                    title="Finding Equivalent Fractions",
                    bullets=[
                        "Denominators: 3 and 4",
                        "Least Common Denominator (LCD) = 12",
                        "1/3 becomes 4/12",
                        "1/4 becomes 3/12",
                    ],
                    narration="Let's find a common multiple for 3 and 4. The least common denominator is 12! Multiplying top and bottom of one third by 4 gives 4 twelfths. Multiplying one fourth by 3 gives 3 twelfths. Now our slices match perfectly!",
                    visual_component="FractionBar",
                    visual_props={"numerator": 4, "denominator": 12, "secondaryNumerator": 3},
                    duration_seconds=9,
                ),
                Slide(
                    slide_number=4,
                    title="Adding the Numerators",
                    bullets=[
                        "Expression: 4/12 + 3/12",
                        "Add tops only: 4 + 3 = 7",
                        "Keep denominator identical: 12",
                        "Total: 7/12 gallon of punch!",
                    ],
                    narration="Step four is easy! Now that both fractions have 12 on the bottom, simply add the tops: 4 plus 3 equals 7. Keep the bottom 12. Together they drank 7 twelfths of a gallon!",
                    visual_component="FractionBar",
                    visual_props={"numerator": 7, "denominator": 12},
                    duration_seconds=8,
                ),
                Slide(
                    slide_number=5,
                    title="Beware the Denominator Trap!",
                    bullets=[
                        "🚫 TRAP: Adding bottom numbers (1/3 + 1/4 ≠ 2/7)",
                        "Denominators describe slice size, not count",
                        "Always keep the common denominator identical",
                    ],
                    narration="Watch out for the sneakiest trap in math! Never add the bottom denominators together. One third plus one fourth is NOT two sevenths! Always keep your common denominator identical.",
                    visual_component="NumberLine",
                    visual_props={"startVal": 0.33, "endVal": 0.58, "min": 0, "max": 1},
                    duration_seconds=8,
                ),
                Slide(
                    slide_number=6,
                    title="Ready for the Quest Arena!",
                    bullets=[
                        "Solve 10 adaptive challenges",
                        "Level up from Easy to Hard",
                        "Claim your Fraction Master badge!",
                    ],
                    narration="Fantastic job! You now possess the power to defeat any fraction with unlike denominators. Step into the arena, solve your practice challenges, and claim your victory badge!",
                    visual_component="TopicGraphic",
                    visual_props={"emoji": "🏆", "label": "Quest Ready"},
                    duration_seconds=7,
                ),
            ]
        else:  # Grade 6
            slides = [
                Slide(
                    slide_number=1,
                    title="Dividing Fractions: Appalachian Trail Adventure",
                    bullets=[
                        "Packing trail mix for a mountain hike",
                        "3/4 pound of trail mix total",
                        "Each snack bag holds 1/8 pound",
                    ],
                    narration="Welcome to Grade 6 Fraction Mastery! You are packing snacks for a hike on Georgia's Appalachian Trail. You have 3 fourths of a pound of trail mix, and each snack bag holds 1 eighth of a pound. How many bags can you fill?",
                    visual_component="TopicGraphic",
                    visual_props={"emoji": "🎒", "label": "Appalachian Trail"},
                    duration_seconds=8,
                ),
                Slide(
                    slide_number=2,
                    title="What Fraction Division Really Means",
                    bullets=[
                        "Division asks: 'How many fit inside?'",
                        "How many 1/8 pieces fit inside 3/4?",
                        "Visual fraction models show the groups",
                    ],
                    narration="Dividing fractions simply asks: how many small groups fit inside the bigger amount? We want to see how many 1 eighth pieces fit into 3 fourths.",
                    visual_component="FractionBar",
                    visual_props={"numerator": 3, "denominator": 4},
                    duration_seconds=8,
                ),
                Slide(
                    slide_number=3,
                    title="The Magic Rule: Keep, Change, Flip!",
                    bullets=[
                        "KEEP the first fraction: 3/4",
                        "CHANGE division (÷) to multiplication (×)",
                        "FLIP the second fraction: 1/8 becomes 8/1",
                    ],
                    narration="Here is the secret weapon: Keep, Change, Flip! Keep the first fraction as 3 fourths. Change division to multiplication. And flip the second fraction upside-down into 8 over 1, its reciprocal!",
                    visual_component="NumberLine",
                    visual_props={"startVal": 0, "endVal": 6, "min": 0, "max": 8},
                    duration_seconds=9,
                ),
                Slide(
                    slide_number=4,
                    title="Multiply Across & Simplify",
                    bullets=[
                        "Multiply tops: 3 × 8 = 24",
                        "Multiply bottoms: 4 × 1 = 4",
                        "Simplify: 24 ÷ 4 = 6 whole snack bags!",
                    ],
                    narration="Now multiply straight across: 3 times 8 equals 24, and 4 times 1 equals 4. 24 divided by 4 equals 6 whole snack bags! You have enough fuel for the entire hike.",
                    visual_component="FractionBar",
                    visual_props={"numerator": 4, "denominator": 4},
                    duration_seconds=8,
                ),
                Slide(
                    slide_number=5,
                    title="Watch Out for the Flip Trap!",
                    bullets=[
                        "🚫 TRAP: Flipping the FIRST fraction",
                        "Always flip ONLY the second fraction (the divisor)",
                        "No common denominator needed for division!",
                    ],
                    narration="Beware of the flip trap! Never flip the first fraction. Only flip the divisor on the right. And remember: you do not need common denominators when doing Keep-Change-Flip!",
                    visual_component="TopicGraphic",
                    visual_props={"emoji": "⚠️", "label": "Trap Alert"},
                    duration_seconds=8,
                ),
                Slide(
                    slide_number=6,
                    title="Claim the Fraction Master Crown!",
                    bullets=[
                        "10 adaptive round challenges",
                        "Streak bonus points available",
                        "Show what you know!",
                    ],
                    narration="You are now officially a fraction division champion! Step into the arena, prove your skills, and let's conquer the leaderboard!",
                    visual_component="TopicGraphic",
                    visual_props={"emoji": "👑", "label": "Victory Arena"},
                    duration_seconds=7,
                ),
            ]

    elif topic_clean == "decimals":
        slides = [
            Slide(
                slide_number=1,
                title="Welcome to Decimals Domain!",
                bullets=[
                    "Shopping at the Atlanta Farmer's Market",
                    "Spending $3.45 on Vidalia onions",
                    "Spending $2.80 on Georgia peaches",
                ],
                narration="Welcome to Decimals Domain! We use decimals every single day, especially with money. Suppose you buy sweet Georgia Vidalia onions for 3 dollars and 45 cents, and fresh peaches for 2 dollars and 80 cents.",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🍑", "label": "Farmer's Market"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=2,
                title="The Golden Rule: Align the Decimal Points",
                bullets=[
                    "Tenths match with tenths",
                    "Hundredths match with hundredths",
                    "Always line up the dots vertically!",
                ],
                narration="The number one rule for adding and subtracting decimals is simple: line up the decimal points vertically! That guarantees tenths line up with tenths, and hundredths with hundredths.",
                visual_component="NumberLine",
                visual_props={"startVal": 0.0, "endVal": 1.0, "min": 0, "max": 2},
                duration_seconds=8,
            ),
            Slide(
                slide_number=3,
                title="Add Like Whole Numbers",
                bullets=[
                    "Hundredths: 5 + 0 = 5",
                    "Tenths: 4 + 8 = 12 (write 2, carry 1)",
                    "Ones: 1 + 3 + 2 = 6",
                    "Total: $6.25",
                ],
                narration="Add each column from right to left just like regular numbers. 5 plus 0 is 5. 4 plus 8 is 12 tenths, so write 2 and carry 1. 1 plus 3 plus 2 equals 6. Bring the decimal straight down: 6 dollars and 25 cents!",
                visual_component="NumberLine",
                visual_props={"startVal": 3.45, "endVal": 6.25, "min": 3, "max": 7},
                duration_seconds=9,
            ),
            Slide(
                slide_number=4,
                title="Placeholder Zeros in Subtraction",
                bullets=[
                    "Problem: 4.50 - 1.65 meters",
                    "Add trailing zeros so columns match",
                    "Borrow across decimals with confidence",
                ],
                narration="When subtracting decimals, always use placeholder zeros! In 4 point 5 0 minus 1 point 6 5, the zero in the hundredths place lets you borrow and subtract accurately to get 2 point 8 5.",
                visual_component="NumberLine",
                visual_props={"startVal": 4.50, "endVal": 2.85, "min": 1, "max": 5},
                duration_seconds=8,
            ),
            Slide(
                slide_number=5,
                title="Beware the Right-Align Trap!",
                bullets=[
                    "🚫 TRAP: Lining numbers up on the right edge",
                    "Never treat decimals as whole numbers without dots",
                    "The decimal point controls the place value!",
                ],
                narration="Watch out for the right-align trap! Don't line numbers up on the right edge. If you don't align the dots, you will add tenths to hundredths and your answer will be way off!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🚫", "label": "Align Dots Always"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=6,
                title="You're Ready for Decimals Quest!",
                bullets=[
                    "Test your place value mastery",
                    "Earn streak bonuses and XP",
                    "Let's jump in!",
                ],
                narration="You are ready to roll! Keep your dots aligned, trust your math, and jump into the practice round to earn maximum XP!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🎯", "label": "Decimals Ready"},
                duration_seconds=7,
            ),
        ]

    elif topic_clean == "ratios":
        slides = [
            Slide(
                slide_number=1,
                title="Welcome to Ratios Realm!",
                bullets=[
                    "Mixing homemade Georgia lemonade",
                    "Ratio: 3 cups lemon juice to 2 cups sugar",
                    "Written as: 3 to 2, 3:2, or 3/2",
                ],
                narration="Welcome to Ratios Realm! A ratio compares two quantities. Picture mixing sweet Georgia lemonade: for every 3 cups of fresh lemon juice, you need 2 cups of sugar. That's a 3 to 2 ratio!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🍋", "label": "Lemonade Recipe"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=2,
                title="Understanding Multiplicative Comparisons",
                bullets=[
                    "Ratios grow by MULTIPLYING, not adding",
                    "Part-to-part: lemon juice to sugar",
                    "Part-to-whole: lemon juice to total punch",
                ],
                narration="Ratios grow through multiplication! If you make a bigger pitcher, you scale up both ingredients by multiplying by the exact same number.",
                visual_component="FractionBar",
                visual_props={"numerator": 3, "denominator": 5},
                duration_seconds=8,
            ),
            Slide(
                slide_number=3,
                title="Scaling Equivalent Ratios",
                bullets=[
                    "Original: 3 cups lemon to 2 cups sugar",
                    "Scale factor = 3 (tripling the recipe)",
                    "3 × 3 = 9 cups lemon",
                    "2 × 3 = 6 cups sugar",
                ],
                narration="Let's make a party batch! If we triple the recipe, multiply both sides by 3: 3 times 3 gives 9 cups of lemon juice, and 2 times 3 gives 6 cups of sugar. The flavor stays perfectly balanced!",
                visual_component="FractionBar",
                visual_props={"numerator": 6, "denominator": 15},
                duration_seconds=9,
            ),
            Slide(
                slide_number=4,
                title="Unit Rates: Price per Single Item",
                bullets=[
                    "Roadside stand: 4 Georgia peaches for $6.00",
                    "Unit Rate formula: Total Cost ÷ Quantity",
                    "$6.00 ÷ 4 = $1.50 per peach",
                ],
                narration="A unit rate tells you how much for ONE single item. At a Macon peach stand, 4 peaches cost 6 dollars. Divide 6 by 4 to discover each peach costs 1 dollar and 50 cents!",
                visual_component="NumberLine",
                visual_props={"startVal": 0, "endVal": 1.5, "min": 0, "max": 3},
                duration_seconds=8,
            ),
            Slide(
                slide_number=5,
                title="Trap Alert: Never Scale by Adding!",
                bullets=[
                    "🚫 TRAP: Adding the same number to both terms",
                    "3:2 + 1 to each does NOT make an equivalent ratio",
                    "Always multiply or divide by the scale factor!",
                ],
                narration="Be on alert! Never scale a ratio by adding. If you add 1 to each term, turning 3 to 2 into 4 to 3, the recipe loses its sweet flavor! Always multiply or divide.",
                visual_component="TopicGraphic",
                visual_props={"emoji": "⚖️", "label": "Multiply Don't Add"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=6,
                title="Unleash Your Ratio Power!",
                bullets=[
                    "Solve real-world proportions",
                    "Earn your Ratio Pro badge",
                    "Start your challenge round!",
                ],
                narration="You have mastered ratio tables and unit rates! Now head into the arena and show your proportional thinking power!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🌟", "label": "Ratio Champion"},
                duration_seconds=7,
            ),
        ]

    elif topic_clean == "factors_multiples":
        slides = [
            Slide(
                slide_number=1,
                title="Welcome to Factors & Multiples!",
                bullets=[
                    "Discovering prime building blocks",
                    "Factor trees and factor pairs",
                    "Our quest: LCM and HCF mastery!",
                ],
                narration="Welcome, math adventurer! Every whole number has secret building blocks called factors. Today we unlock prime numbers, factor trees, and the superpowers of LCM and HCF!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🔢", "label": "Prime Numbers & Factors"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=2,
                title="Primes vs. Composites",
                bullets=[
                    "Prime numbers have exactly 2 factors: 1 and itself",
                    "1 is neither prime nor composite",
                    "2 is the ONLY even prime number!",
                ],
                narration="A prime number can only be divided by 1 and itself, like 2, 3, 5, and 7. Remember: the number 1 is not prime because it only has one single factor!",
                visual_component="NumberLine",
                visual_props={"startVal": 2, "endVal": 7, "min": 1, "max": 10},
                duration_seconds=8,
            ),
            Slide(
                slide_number=3,
                title="Prime Factorization Trees",
                bullets=[
                    "Break numbers down until only primes remain",
                    "Example: 12 = 2 × 2 × 3",
                    "Every composite number has a unique prime fingerprint!",
                ],
                narration="To find the prime factorization, branch the number into factor pairs until all branches end in prime numbers. For 12, that's 2 times 2 times 3. That is its unique prime fingerprint!",
                visual_component="FractionBar",
                visual_props={"numerator": 2, "denominator": 6},
                duration_seconds=9,
            ),
            Slide(
                slide_number=4,
                title="Finding LCM and HCF",
                bullets=[
                    "HCF (GCD): Greatest factor shared by both numbers",
                    "LCM: Smallest positive common multiple",
                    "Example: 4 and 6 -> LCM is 12, HCF is 2",
                ],
                narration="For any pair of numbers, the Highest Common Factor is the largest shared divisor, and the Lowest Common Multiple is the first spot their multiples meet on the number line!",
                visual_component="NumberLine",
                visual_props={"startVal": 4, "endVal": 12, "min": 0, "max": 15},
                duration_seconds=8,
            ),
            Slide(
                slide_number=5,
                title="Trap Alert: Primes vs Odds!",
                bullets=[
                    "🚫 TRAP: Assuming all odd numbers are prime",
                    "Numbers like 9, 15, and 21 are composite (3 × 3 = 9)",
                    "Always test for divisibility!",
                ],
                narration="Watch out for the odd number trap! Not every odd number is prime. For instance, 9 can be broken into 3 times 3, and 15 is 3 times 5. Always check for factors!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🚫", "label": "Divisibility Check"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=6,
                title="Prime Time Ready!",
                bullets=[
                    "Factor trees and multiples conquered",
                    "Earn your CBSE Champion badge",
                    "Step into the arena!",
                ],
                narration="You have cracked the code of factors and multiples! Jump into the challenge round, build your streak, and earn your trophy!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🌟", "label": "Factors Champion"},
                duration_seconds=7,
            ),
        ]

    elif topic_clean == "integers":
        slides = [
            Slide(
                slide_number=1,
                title="Welcome to the Integer Frontier!",
                bullets=[
                    "Numbers below zero in the freezing mountains",
                    "Positive, negative, and zero",
                    "Our quest: Number line navigation!",
                ],
                narration="Welcome to the Integer Frontier! Numbers don't stop at zero. When temperatures plummet below freezing or submarines dive into the ocean, negative integers come to the rescue!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🏔️", "label": "Below Zero Navigation"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=2,
                title="What Are Integers?",
                bullets=[
                    "Whole numbers and their opposites",
                    "Zero is the origin: neither positive nor negative",
                    "Opposite of +5 is -5",
                ],
                narration="Integers are all positive whole numbers, negative whole numbers, and zero. Every positive number has an opposite partner across zero on the number line!",
                visual_component="NumberLine",
                visual_props={"startVal": -5, "endVal": 5, "min": -6, "max": 6},
                duration_seconds=8,
            ),
            Slide(
                slide_number=3,
                title="Walking the Integer Number Line",
                bullets=[
                    "Moving RIGHT means adding or increasing",
                    "Moving LEFT means subtracting or decreasing",
                    "-10 is smaller than -2!",
                ],
                narration="Think of the number line as a hiking trail: moving right always means getting bigger, and moving left means getting smaller. Even though 10 is big, negative 10 is way to the left, so it is smaller than negative 2!",
                visual_component="NumberLine",
                visual_props={"startVal": -4, "endVal": 3, "min": -5, "max": 5},
                duration_seconds=9,
            ),
            Slide(
                slide_number=4,
                title="Adding Integers: Like vs Unlike Signs",
                bullets=[
                    "Same signs: Add the values and keep the sign (-3 + -4 = -7)",
                    "Different signs: Subtract the values and take the sign of the larger distance",
                    "Example: -5 + 8 = +3",
                ],
                narration="When signs are the same, join them together and keep the sign! When signs are different, find the difference between their distances and keep the sign of the bigger team!",
                visual_component="NumberLine",
                visual_props={"startVal": -5, "endVal": 3, "min": -6, "max": 6},
                duration_seconds=8,
            ),
            Slide(
                slide_number=5,
                title="Trap Alert: Addition vs Multiplication Signs!",
                bullets=[
                    "🚫 TRAP: Thinking two negatives always make a positive",
                    "In addition: (-3) + (-4) = -7, NOT +7",
                    "Two debts make a bigger debt!",
                ],
                narration="Beware the double-negative trap! Two negatives only multiply to make a positive. When adding debts, two negatives combine into a bigger negative!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🚫", "label": "Debts Combine Negative"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=6,
                title="Master the Integer Realm!",
                bullets=[
                    "Direction and distance mastered",
                    "Conquer absolute values and sums",
                    "Begin your quest now!",
                ],
                narration="You are now a master of positive and negative numbers! Step into the quest, solve your challenges, and conquer the Integer Frontier!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "⚡", "label": "Integer Pro"},
                duration_seconds=7,
            ),
        ]

    else:  # geometry
        slides = [
            Slide(
                slide_number=1,
                title="Welcome to Geometry Citadel!",
                bullets=[
                    "Planning community gardens in Savannah",
                    "Measuring perimeter for fencing",
                    "Measuring area for fertile soil",
                ],
                narration="Welcome to Geometry Citadel! Geometry helps us build real things. Imagine planning a community garden in Savannah: you need fencing for the outside perimeter, and fertile soil for the area inside!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "📐", "label": "Savannah Garden"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=2,
                title="Perimeter vs Area: Fence vs Floor",
                bullets=[
                    "Perimeter (P): distance all the way AROUND",
                    "Formula: P = 2 × (length + width)",
                    "Area (A): flat surface space INSIDE",
                    "Formula: A = length × width",
                ],
                narration="Remember the difference: Perimeter is the fence around the edge, measured in linear feet. Area is the carpet covering the inside floor, measured in square feet!",
                visual_component="ShapeDiagram",
                visual_props={"shape": "rectangle", "width": 8, "height": 5, "highlight": "perimeter"},
                duration_seconds=9,
            ),
            Slide(
                slide_number=3,
                title="Rectangle Calculations",
                bullets=[
                    "Garden plot: Length = 8 ft, Width = 5 ft",
                    "Perimeter: 2 × (8 + 5) = 26 feet of fence",
                    "Area: 8 × 5 = 40 square feet of soil",
                ],
                narration="For our garden measuring 8 by 5 feet, the perimeter is 2 times 13, which is 26 feet of fence. The area is 8 times 5, which equals 40 square feet of planting soil!",
                visual_component="ShapeDiagram",
                visual_props={"shape": "rectangle", "width": 8, "height": 5, "highlight": "area"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=4,
                title="Triangle Area: Half a Rectangle!",
                bullets=[
                    "Every triangle is exactly HALF of a rectangle",
                    "Formula: Area = (base × height) ÷ 2",
                    "Sail on Lake Lanier: Base = 8m, Height = 5m",
                    "Area: (8 × 5) ÷ 2 = 20 square meters",
                ],
                narration="Here is a mind-blowing secret: every triangle is exactly half of a rectangle! That's why the formula is base times height divided by 2. An 8 by 5 meter sail has an area of 40 divided by 2, which is 20 square meters!",
                visual_component="ShapeDiagram",
                visual_props={"shape": "triangle", "width": 8, "height": 5, "highlight": "area"},
                duration_seconds=9,
            ),
            Slide(
                slide_number=5,
                title="Trap Alert: Don't Forget to Divide by 2!",
                bullets=[
                    "🚫 TRAP: Forgetting to divide by 2 for triangles",
                    "Base times height gives the whole rectangle",
                    "Always take half for the triangle!",
                ],
                narration="Avoid the number one geometry mistake: never forget to divide by 2 when finding triangle area! Base times height gives the whole box—you must cut it in half for the triangle.",
                visual_component="ShapeDiagram",
                visual_props={"shape": "triangle", "width": 12, "height": 7, "highlight": "area"},
                duration_seconds=8,
            ),
            Slide(
                slide_number=6,
                title="Conquer the Citadel!",
                bullets=[
                    "Area, perimeter, and volume mastered",
                    "10 adaptive challenges waiting",
                    "Start your quest now!",
                ],
                narration="You are equipped with the architect's toolkit! Step into the practice arena, solve your challenges, and conquer Geometry Citadel!",
                visual_component="TopicGraphic",
                visual_props={"emoji": "🏛️", "label": "Citadel Master"},
                duration_seconds=7,
            ),
        ]

    return ScriptResponse(
        topic=topic_clean,
        grade=grade,
        title=f"Grade {grade} {topic_clean.capitalize()} Video Masterclass",
        standard_code=standard_code,
        slides=slides,
        cached=False,
    )


def get_topic_script(grade: int, topic: str) -> ScriptResponse:
    """Retrieve or generate 6-slide educational video script, enforcing caching."""
    topic_clean = topic.lower().strip()
    cache_key = f"{grade}_{topic_clean}"
    local_cache = _load_cache()

    # 1. Check cache
    if cache_key in local_cache:
        try:
            cached_data = local_cache[cache_key].copy()
            cached_data["cached"] = True
            logger.info("Serving video script from cache for %s", cache_key)
            return ScriptResponse.model_validate(cached_data)
        except Exception as exc:
            logger.warning("Cached script invalid for %s: %s", cache_key, exc)

    # 2. Get top standard code
    standards = retrieve_standards(query=topic_clean, topic=topic_clean, grade=grade, limit=1)
    std_code = standards[0]["code"] if standards else f"MGSE{grade}"

    # 3. Dynamic generation with Gemini if available
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL")

    if gemini_key and gemini_model:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            prompt = f"""You are MathQuest Georgia's expert educational video producer.
Create a structured 6-slide video presentation script for Grade {grade} on '{topic_clean}' aligned to Georgia standard {std_code}.

REQUIREMENTS:
1. title: Engaging video title.
2. standard_code: Must be {std_code}.
3. slides: EXACTLY 6 slides.
   - Slide 1: Welcome & Real-World Georgia Hook (narration, 3 bullets, visual_component: TopicGraphic)
   - Slide 2: Core Concept Definition (narration, 3 bullets, visual_component: FractionBar, NumberLine, or ShapeDiagram)
   - Slide 3: Visual Model Exploration (narration, 3-4 bullets, visual_component with visual_props)
   - Slide 4: Worked Example Step-by-Step with mathematically correct numbers (narration, 4 bullets)
   - Slide 5: Beware of the Misconception Trap (narration, 3 bullets, warning what NOT to do)
   - Slide 6: Cheerful Wrap-up & Practice Challenge (narration, 3 bullets, visual_component: TopicGraphic)
"""
            response = client.models.generate_content(
                model=gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=_LLMScriptSchema,
                    temperature=0.2,
                ),
            )
            raw = json.loads(response.text)
            parsed = _LLMScriptSchema.model_validate(raw)

            if len(parsed.slides) == 6:
                slides_objs = [
                    Slide(
                        slide_number=idx + 1,
                        title=s.title,
                        bullets=s.bullets,
                        narration=s.narration,
                        visual_component=s.visual_component or "TopicGraphic",
                        visual_props=s.visual_props or {},
                        duration_seconds=s.duration_seconds or 8,
                    )
                    for idx, s in enumerate(parsed.slides)
                ]
                result = ScriptResponse(
                    topic=topic_clean,
                    grade=grade,
                    title=parsed.title,
                    standard_code=parsed.standard_code or std_code,
                    slides=slides_objs,
                    cached=False,
                )
                local_cache[cache_key] = result.model_dump()
                _save_cache(local_cache)
                return result
        except Exception as exc:
            logger.warning("Dynamic Gemini script generation failed: %s. Using curated verified script.", exc)

    # 4. Fallback to curated, verified 6-slide script
    result = _get_curated_script(grade=grade, topic=topic_clean, standard_code=std_code)
    local_cache[cache_key] = result.model_dump()
    _save_cache(local_cache)
    return result
