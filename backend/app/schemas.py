"""Pydantic v2 schemas for MathQuest Georgia.

Defines domain models for difficulty tiers, answer options, questions,
LLM question generation templates, and student answer evaluation.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Tier(str, Enum):
    """Difficulty tiers for adaptive question delivery."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MathTopic(str, Enum):
    """Curriculum math domain topics aligned with Georgia Standards (MGSE) and CBSE."""

    FRACTIONS = "fractions"
    DECIMALS = "decimals"
    RATIOS = "ratios"
    GEOMETRY = "geometry"
    FACTORS_MULTIPLES = "factors_multiples"
    INTEGERS = "integers"


class Option(BaseModel):
    """Multiple-choice option for a question.
    
    Distractors may include an optional misconception_tag derived
    from the curated misconception library.
    """

    model_config = ConfigDict(extra="forbid")

    id: Annotated[str, Field(description="Identifier for the option, e.g. 'A', 'B', 'C', 'D'")]
    text: Annotated[str, Field(description="Answer text or numerical value presented to the student")]
    misconception_tag: Annotated[
        str | None,
        Field(
            default=None,
            description="Diagnostic tag explaining the specific conceptual error, if applicable",
        ),
    ] = None


class Question(BaseModel):
    """Fully verified question delivered to the student."""

    model_config = ConfigDict(extra="forbid")

    id: Annotated[str, Field(description="Unique question identifier")]
    board: Annotated[
        str,
        Field(
            default="georgia",
            description="Curriculum board identifier, e.g. 'georgia', 'cbse'",
        ),
    ] = "georgia"
    topic: Annotated[str, Field(description="Math topic, e.g. 'fractions', 'decimals', 'measurement'")]
    grade: Annotated[int, Field(ge=5, le=6, description="Target grade level (5 or 6)")]
    tier: Annotated[Tier, Field(description="Difficulty tier")]
    stem: Annotated[str, Field(description="The word problem or narrative question stem")]
    expression: Annotated[str, Field(description="The underlying mathematical expression or problem")]
    options: Annotated[list[Option], Field(min_length=2, description="Multiple-choice options list")]
    correct_option_id: Annotated[str, Field(description="ID of the correct option")]
    explanation: Annotated[str, Field(description="Child-friendly, step-by-step solution walkthrough")]
    standard_code: Annotated[
        str,
        Field(description="Curriculum standard code, e.g. 'MGSE5.NF.1' or 'CBSE6.MATH.01'"),
    ]

    @model_validator(mode="after")
    def check_correct_option_in_options(self) -> Question:
        """Ensure correct_option_id references an existing option in options."""
        option_ids = {opt.id for opt in self.options}
        if self.correct_option_id not in option_ids:
            raise ValueError(
                f"correct_option_id '{self.correct_option_id}' not found in options: {sorted(option_ids)}"
            )
        return self


class QuestionType(str, Enum):
    """Categorical classification of the mathematical problem mechanics."""

    FRACTION_ADD_SUB = "fraction_add_sub"
    FRACTION_MUL_DIV = "fraction_mul_div"
    DECIMAL_OPS = "decimal_ops"
    RATIO = "ratio"
    GEOMETRY_AREA_PERIMETER = "geometry_area_perimeter"
    FACTORS_MULTIPLES = "factors_multiples"
    LCM_GCD = "lcm_gcd"
    INTEGERS = "integers"


class QuestionTemplate(BaseModel):
    """Schema returned by the LLM before mathematical verification and distractor generation.

    The LLM provides the creative narrative stem, the mathematical expression, standard,
    topic, tier, specific question_type, operands list, and claimed_answer.
    Verification compares verify.evaluate(expression) to claimed_answer using exact Fraction equality.
    """

    model_config = ConfigDict(extra="forbid")

    board: Annotated[
        str,
        Field(
            default="georgia",
            description="Curriculum board identifier, e.g. 'georgia', 'cbse'",
        ),
    ] = "georgia"
    stem: Annotated[str, Field(description="The narrative scenario or word problem")]
    expression: Annotated[str, Field(description="Exact mathematical expression to compute/solve")]
    standard_code: Annotated[
        str,
        Field(description="Curriculum standard code (e.g. 'MGSE5.NF.1' or 'CBSE6.MATH.01')"),
    ]
    topic: Annotated[str, Field(description="Math domain topic, e.g. 'fractions'")]
    tier: Annotated[Tier, Field(description="Target difficulty tier")]
    question_type: Annotated[
        QuestionType,
        Field(
            default=QuestionType.FRACTION_ADD_SUB,
            description="Type of math problem: fraction_add_sub, fraction_mul_div, decimal_ops, ratio, geometry_area_perimeter, factors_multiples, lcm_gcd, integers",
        ),
    ]
    operands: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of operand numbers or fractions as strings, e.g. ['3/4', '1/2']",
        ),
    ]
    claimed_answer: Annotated[
        str,
        Field(
            default="",
            description="The answer claimed by the LLM to verify against the evaluated expression",
        ),
    ]


class AnswerSubmission(BaseModel):
    """Payload submitted by the frontend when a student selects an answer."""

    model_config = ConfigDict(extra="ignore")

    question_id: Annotated[str, Field(min_length=1, max_length=100, description="ID of the question being answered")]
    selected_option_id: Annotated[str, Field(min_length=1, max_length=10, description="ID of the option chosen by the student")]
    time_taken_seconds: Annotated[
        float | None,
        Field(default=None, ge=0.0, le=3600.0, description="Optional time spent answering in seconds"),
    ] = None
    board: Annotated[
        str,
        Field(
            default="georgia",
            description="Curriculum board identifier, e.g. 'georgia', 'cbse'",
        ),
    ] = "georgia"
    topic: Annotated[str | None, Field(default=None, description="Topic of the question")] = None
    tier: Annotated[Tier, Field(default=Tier.MEDIUM, description="Current difficulty tier")] = Tier.MEDIUM
    hints_used: Annotated[int, Field(default=0, ge=0, le=3, description="Number of hints used on this problem (0-3)")] = 0
    streak: Annotated[int, Field(default=0, ge=0, description="Current consecutive correct answer streak")] = 0
    history: list[bool] = Field(default_factory=list, description="Recent answer history booleans")
    current_mastery: Annotated[float, Field(default=50.0, ge=0.0, le=100.0, description="Current topic mastery score (0-100)")] = 50.0
    session_stats: dict = Field(default_factory=dict, description="Session statistics for badge tracking")
    correct_option_id: Annotated[str | None, Field(default=None, description="Optional correct option ID override for client-stored questions")] = None

    options: Annotated[list[Option] | None, Field(default=None, description="Optional list of question options")] = None
    explanation: Annotated[str | None, Field(default=None, description="Optional explanation override")] = None


class AnswerResult(BaseModel):
    """Response returned after evaluating a student's answer submission."""

    model_config = ConfigDict(extra="ignore")

    is_correct: Annotated[bool, Field(description="Whether the submitted answer was correct")]
    correct_option_id: Annotated[str, Field(description="ID of the correct option")]
    correct_answer: Annotated[str, Field(default="", description="Text representation of the correct answer")] = ""
    explanation: Annotated[str, Field(description="Encouraging step-by-step explanation")]
    misconception_tag: Annotated[
        str | None,
        Field(
            default=None,
            description="Tag identifying the conceptual error if a tagged distractor was picked",
        ),
    ] = None
    misconception_feedback: Annotated[
        str | None,
        Field(
            default=None,
            description="Child-friendly hint addressing the specific misconception",
        ),
    ] = None
    points: Annotated[int, Field(default=0, ge=0, description="Gamified points awarded for this problem")] = 0
    xp_earned: Annotated[int, Field(default=0, ge=0, description="Gamified XP points awarded (alias for points)")] = 0
    next_tier: Annotated[Tier, Field(default=Tier.MEDIUM, description="Recommended tier for the next question")] = Tier.MEDIUM
    new_mastery: Annotated[float, Field(default=50.0, ge=0, le=100, description="Updated topic mastery score (0-100)")] = 50.0
    new_badges: list[str] = Field(default_factory=list, description="Newly unlocked badges")
    streak: Annotated[int, Field(default=0, ge=0, description="Updated consecutive correct answer streak")] = 0
    board: Annotated[str, Field(default="georgia", description="Curriculum board identifier")] = "georgia"




class QuestionRequest(BaseModel):
    """Request payload to generate a new adaptive question or batch of questions."""

    model_config = ConfigDict(extra="forbid")

    board: Annotated[
        str,
        Field(
            default="georgia",
            description="Curriculum board identifier, e.g. 'georgia', 'cbse'",
        ),
    ] = "georgia"
    grade: Annotated[int, Field(ge=5, le=6, default=5, description="Grade level: 5 or 6")]
    topic: Annotated[MathTopic, Field(default=MathTopic.FRACTIONS, description="Topic: fractions, decimals, ratios, geometry, factors_multiples, integers")]
    tier: Annotated[Tier, Field(default=Tier.MEDIUM, description="Difficulty tier: easy, medium, hard")]
    count: Annotated[int, Field(ge=1, le=10, default=1, description="Number of questions to generate (1 to 10 for a round)")] = 1

    @field_validator("topic", mode="before")
    @classmethod
    def normalize_topic(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class BatchQuestionResponse(BaseModel):
    """Batch question response payload for a full game round."""

    model_config = ConfigDict(extra="forbid")

    questions: Annotated[list[Question], Field(description="List of verified questions for the round")]
    count: Annotated[int, Field(description="Total questions generated")]
    topic: Annotated[str, Field(description="Topic for the round")]
    tier: Annotated[Tier, Field(description="Difficulty tier")]



class HealthResponse(BaseModel):
    """Health status response payload."""

    status: str = Field(default="ok", description="Health status string")
    app: str = Field(default="MathQuest Georgia API", description="Service name")
    version: str = Field(default="0.1.0", description="API version")


class ExplainStyle(str, Enum):
    """Pedagogical explanation style."""

    DEFAULT = "default"
    SIMPLER = "simpler"
    REAL_LIFE = "real_life"
    STEP_BY_STEP = "step_by_step"


class WorkedExample(BaseModel):
    """Step-by-step worked problem example with mathematically verified answer."""

    model_config = ConfigDict(extra="ignore")

    problem: Annotated[str, Field(description="Word problem or contextual math problem statement")]
    expression: Annotated[str, Field(description="Mathematical expression to evaluate")]
    steps: Annotated[list[str], Field(description="Clear, numbered steps leading to the answer")]
    verified_answer: Annotated[str, Field(description="The verified final answer computed by verify.py")]


class ExplainRequest(BaseModel):
    """Request payload for pedagogical concept explanation."""

    model_config = ConfigDict(extra="forbid")

    grade: Annotated[int, Field(ge=5, le=6, default=5, description="Grade level: 5 or 6")]
    topic: Annotated[MathTopic, Field(default=MathTopic.FRACTIONS, description="fractions, decimals, ratios, or geometry")]
    style: Annotated[ExplainStyle, Field(default=ExplainStyle.DEFAULT, description="Explanation style")]

    @field_validator("topic", mode="before")
    @classmethod
    def normalize_topic(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class ExplainResponse(BaseModel):
    """Structured educational response for topic learning."""

    model_config = ConfigDict(extra="ignore")

    title: Annotated[str, Field(description="Engaging headline for the topic")]
    intro: Annotated[str, Field(description="Child-friendly introductory concept explanation")]
    key_ideas: Annotated[list[str], Field(description="Bullet points of crucial conceptual rules")]
    worked_examples: Annotated[list[WorkedExample], Field(min_length=2, max_length=2, description="Exactly 2 worked examples")]
    common_mistakes: Annotated[list[str], Field(description="Common pitfalls and misconceptions")]
    standard_code: Annotated[str, Field(description="Aligned Georgia MGSE code")]
    standard_snippet: Annotated[str, Field(default="", description="Short snippet of the aligned MGSE standard")]
    topic: Annotated[str, Field(description="Subject topic")]
    grade: Annotated[int, Field(description="Target grade")]
    style: Annotated[ExplainStyle, Field(description="Explanation style requested")]
    cached: Annotated[bool, Field(default=False, description="Whether returned from cache")]


class InfographicResponse(BaseModel):
    """Topic educational infographic image payload."""

    topic: Annotated[str, Field(description="Topic identifier")]
    grade: Annotated[int, Field(default=5, description="Grade level")]
    image_url: Annotated[str, Field(description="Pollinations.ai generated image URL")]
    url: Annotated[str, Field(description="Direct image URL")]
    fallback_url: Annotated[str, Field(description="Local SVG fallback image path")]
    prompt: Annotated[str, Field(description="Prompt used for the image generation")]
    format: Annotated[str, Field(default="svg", description="Format descriptor")] = "svg"
    source: Annotated[str, Field(default="cache", description="Source descriptor")] = "cache"
    local_path: Annotated[str, Field(default="", description="Path to local cached file if available")] = ""


class Slide(BaseModel):
    """Single slide in the educational video script."""

    model_config = ConfigDict(extra="ignore")

    slide_number: Annotated[int, Field(ge=1, le=6, description="Slide sequence number (1 to 6)")]
    title: Annotated[str, Field(description="Slide headline")]
    bullets: Annotated[list[str], Field(description="Key bullet points displayed on the slide")]
    narration: Annotated[str, Field(description="Child-friendly spoken script for speech synthesis")]
    visual_component: Annotated[
        str,
        Field(
            default="TopicGraphic",
            description="Name of the visual component: FractionBar, NumberLine, ShapeDiagram, or TopicGraphic",
        ),
    ]
    visual_props: Annotated[
        dict[str, Any],
        Field(default_factory=dict, description="Props passed into the visual component"),
    ]
    duration_seconds: Annotated[int, Field(default=8, ge=3, le=30, description="Estimated duration in seconds")] = 8


class ScriptRequest(BaseModel):
    """Request payload for topic video script."""

    model_config = ConfigDict(extra="forbid")

    grade: Annotated[int, Field(ge=5, le=6, default=5, description="Grade level: 5 or 6")]
    topic: Annotated[MathTopic, Field(default=MathTopic.FRACTIONS, description="fractions, decimals, ratios, or geometry")]

    @field_validator("topic", mode="before")
    @classmethod
    def normalize_topic(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class ScriptResponse(BaseModel):
    """6-slide educational video script payload."""

    model_config = ConfigDict(extra="ignore")

    topic: Annotated[str, Field(description="Topic identifier")]
    grade: Annotated[int, Field(description="Grade level")]
    title: Annotated[str, Field(description="Overall video presentation title")]
    standard_code: Annotated[str, Field(description="Curriculum standard code")]
    slides: Annotated[list[Slide], Field(min_length=6, max_length=6, description="Exactly 6 slide objects")]
    cached: Annotated[bool, Field(default=False, description="Whether returned from cache")] = False


# ============================================================================
# Curriculum Pack Models (Extensibility for Multi-Board Support)
# ============================================================================

class TierRule(BaseModel):
    """Configuration rule for a difficulty tier within a topic."""

    model_config = ConfigDict(extra="forbid")

    tier: Annotated[Tier, Field(description="Difficulty tier (easy, medium, hard)")]
    description: Annotated[str, Field(description="Pedagogical description of this tier")]
    operands_range: Annotated[
        dict[str, Any],
        Field(default_factory=dict, description="Allowed operand constraints and ranges"),
    ]
    example_expression: Annotated[
        str,
        Field(default="", description="Representative example expression"),
    ]


class TopicConfig(BaseModel):
    """Configuration for a curriculum topic within a curriculum pack."""

    model_config = ConfigDict(extra="forbid")

    id: Annotated[str, Field(description="Unique topic identifier, e.g. 'fractions', 'factors_multiples'")]
    title: Annotated[str, Field(description="Human-readable title")]
    description: Annotated[str, Field(description="Summary of the topic scope")]
    standard_code: Annotated[
        str,
        Field(description="Primary aligned standard code, e.g. 'MGSE5.NF.1' or 'CBSE6.MATH.01'"),
    ]
    standard_title: Annotated[
        str,
        Field(default="", description="Title or summary of the aligned standard"),
    ]
    verified: Annotated[
        bool,
        Field(default=True, description="Whether the curriculum alignment has been verified"),
    ]
    tier_rules: Annotated[
        dict[str, TierRule],
        Field(
            default_factory=dict,
            description="Rules mapped by tier string ('easy', 'medium', 'hard')",
        ),
    ]


class CurriculumPack(BaseModel):
    """Curriculum pack defining a board and grade's learning roadmap and standards."""

    model_config = ConfigDict(extra="forbid")

    board: Annotated[str, Field(description="Board identifier code, e.g. 'georgia', 'cbse'")]
    board_name: Annotated[
        str,
        Field(
            description="Human-readable board name, e.g. 'Georgia Standards of Excellence (MGSE)'",
        ),
    ]
    grade: Annotated[int, Field(ge=1, le=12, description="Target grade level")]
    version: Annotated[str, Field(default="1.0.0", description="Pack version string")]
    verified: Annotated[
        bool,
        Field(default=True, description="Overall verification status of standards in pack"),
    ]
    topics: Annotated[
        list[TopicConfig],
        Field(min_length=1, description="List of topics included in the pack"),
    ]

    def get_topic(self, topic_id: str) -> TopicConfig | None:
        """Retrieve topic configuration by ID."""
        for topic in self.topics:
            if topic.id == topic_id:
                return topic
        return None
