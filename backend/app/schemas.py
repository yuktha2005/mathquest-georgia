"""Pydantic v2 schemas for MathQuest Georgia.

Defines domain models for difficulty tiers, answer options, questions,
LLM question generation templates, and student answer evaluation.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Tier(str, Enum):
    """Difficulty tiers for adaptive question delivery."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


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
        Field(description="Georgia Standards of Excellence (MGSE) code, e.g. 'MGSE5.NF.1'"),
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


class QuestionTemplate(BaseModel):
    """Schema returned by the LLM before mathematical verification and distractor generation.

    The LLM provides the creative narrative stem, the mathematical expression, standard,
    topic, tier, specific question_type, operands list, and claimed_answer.
    Verification compares verify.evaluate(expression) to claimed_answer using exact Fraction equality.
    """

    model_config = ConfigDict(extra="forbid")

    stem: Annotated[str, Field(description="The narrative scenario or word problem")]
    expression: Annotated[str, Field(description="Exact mathematical expression to compute/solve")]
    standard_code: Annotated[
        str,
        Field(description="Georgia Standards of Excellence code (e.g. 'MGSE5.NF.1')"),
    ]
    topic: Annotated[str, Field(description="Math domain topic, e.g. 'fractions'")]
    tier: Annotated[Tier, Field(description="Target difficulty tier")]
    question_type: Annotated[
        QuestionType,
        Field(
            default=QuestionType.FRACTION_ADD_SUB,
            description="Type of math problem: fraction_add_sub, fraction_mul_div, decimal_ops, ratio, geometry_area_perimeter",
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

    model_config = ConfigDict(extra="forbid")

    question_id: Annotated[str, Field(description="ID of the question being answered")]
    selected_option_id: Annotated[str, Field(description="ID of the option chosen by the student")]
    time_taken_seconds: Annotated[
        float | None,
        Field(default=None, ge=0, description="Optional time spent answering in seconds"),
    ] = None


class AnswerResult(BaseModel):
    """Response returned after evaluating a student's answer submission."""

    model_config = ConfigDict(extra="forbid")

    is_correct: Annotated[bool, Field(description="Whether the submitted answer was correct")]
    correct_option_id: Annotated[str, Field(description="ID of the correct option")]
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
    xp_earned: Annotated[int, Field(default=0, ge=0, description="Gamified XP points awarded")]


class QuestionRequest(BaseModel):
    """Request payload to generate a new adaptive question or batch of questions."""

    model_config = ConfigDict(extra="forbid")

    grade: Annotated[int, Field(ge=5, le=6, default=5, description="Grade level: 5 or 6")]
    topic: Annotated[str, Field(default="fractions", description="Topic: fractions, decimals, ratios, geometry")]
    tier: Annotated[Tier, Field(default=Tier.MEDIUM, description="Difficulty tier: easy, medium, hard")]
    count: Annotated[int, Field(ge=1, le=10, default=1, description="Number of questions to generate (1 to 10 for a round)")] = 1


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

