"""Evaluation runner benchmarking question generation and verification accuracy.

Configurable sample size N (defaults to 3, or read from EVAL_N env var).
Saves evaluation metrics and detailed test results to backend/eval/results.json.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import time

from app.schemas import Tier
from app.services.question_builder import build_question_pipeline

logger = logging.getLogger(__name__)

EVAL_DIR = Path(__file__).resolve().parent
RESULTS_FILE = EVAL_DIR / "results.json"


def get_eval_n() -> int:
    """Read configurable evaluation sample size N, defaulting to 3."""
    try:
        return int(os.getenv("EVAL_N", 3))
    except ValueError:
        return 3


def run_evaluation(
    n: int | None = None,
    mock_llm=None,
) -> dict:
    """Run evaluation benchmark for question generation and mathematical verification.

    Args:
        n: Number of samples per topic (defaults to get_eval_n() = 3).
        mock_llm: Optional mock function for LLM during automated tests.

    Returns:
        Summary metrics dictionary, also saved to backend/eval/results.json.
    """
    sample_count = n if n is not None else get_eval_n()
    topics = ["fractions", "decimals", "ratios", "geometry"]
    tiers = [Tier.EASY, Tier.MEDIUM, Tier.HARD]

    results: list[dict] = []
    total_latency = 0.0
    passed_verification = 0
    total_retries = 0
    fallback_count = 0

    start_eval_time = time.perf_counter()

    for i in range(sample_count):
        topic = topics[i % len(topics)]
        tier = tiers[i % len(tiers)]
        grade = 5 if i % 2 == 0 else 6

        kwargs = {"llm_func": mock_llm} if mock_llm else {}
        q, retries, latency_ms, used_fallback = build_question_pipeline(
            grade=grade,
            topic=topic,
            tier=tier,
            **kwargs,
        )

        total_latency += latency_ms
        total_retries += retries
        if used_fallback:
            fallback_count += 1
        else:
            passed_verification += 1

        results.append({
            "run_index": i + 1,
            "grade": grade,
            "topic": topic,
            "tier": tier.value,
            "question_id": q.id,
            "expression": q.expression,
            "correct_option_id": q.correct_option_id,
            "retries": retries,
            "latency_ms": round(latency_ms, 2),
            "used_fallback": used_fallback,
        })

    total_runs = len(results)
    avg_latency = round(total_latency / total_runs, 2) if total_runs else 0.0
    pass_rate = round((passed_verification / total_runs) * 100, 1) if total_runs else 100.0

    eval_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "eval_n": sample_count,
        "total_evaluated": total_runs,
        "pass_rate_percentage": pass_rate,
        "fallback_rate_percentage": round((fallback_count / total_runs) * 100, 1) if total_runs else 0.0,
        "avg_latency_ms": avg_latency,
        "total_retries": total_retries,
        "status": "success",
        "samples": results,
    }

    # Save results to file
    RESULTS_FILE.write_text(json.dumps(eval_data, indent=2), encoding="utf-8")
    logger.info("Evaluation complete for N=%d. Saved to %s", sample_count, RESULTS_FILE)
    return eval_data


def load_evaluation_results() -> dict:
    """Load latest saved evaluation results from disk, running an initial eval if not found."""
    if not RESULTS_FILE.exists():
        logger.info("results.json not found. Generating initial evaluation with N=%d", get_eval_n())
        return run_evaluation(n=get_eval_n())

    try:
        return json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Error reading results.json (%s). Re-running evaluation.", exc)
        return run_evaluation(n=get_eval_n())
