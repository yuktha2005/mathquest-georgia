"""Evaluation metrics router reading from backend/eval/results.json."""

from fastapi import APIRouter, Query
from eval.runner import get_eval_n, load_evaluation_results, run_evaluation

router = APIRouter(tags=["evaluation"])


@router.get("/api/eval")
def get_evaluation_metrics():
    """Read the latest evaluation results from the saved file backend/eval/results.json."""
    return load_evaluation_results()


@router.post("/api/eval/run")
def trigger_evaluation(
    n: int = Query(default=3, ge=1, le=50, description="Evaluation sample size N (default 3)"),
):
    """Trigger a new evaluation run with configurable N and save results to file."""
    return run_evaluation(n=n)
