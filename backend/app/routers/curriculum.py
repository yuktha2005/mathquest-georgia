"""Curriculum API endpoints.

Provides endpoints to list available boards, grades, topics, and full curriculum packs.
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, Query, Request

from app.limiter import limiter
from app.schemas import CurriculumPack, TopicConfig
from app.services.curriculum import (
    CurriculumPackNotFoundError,
    curriculum_service,
)

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])


@router.get("/packs", response_model=list[CurriculumPack])
@limiter.limit("60/minute")
def get_all_packs(request: Request) -> list[CurriculumPack]:
    """Retrieve all available curriculum packs across all boards and grades."""
    return curriculum_service.list_packs()


@router.get("/pack/{board}/{grade}", response_model=CurriculumPack)
@limiter.limit("60/minute")
def get_pack_by_board_and_grade(
    request: Request,
    board: str,
    grade: int,
) -> CurriculumPack:
    """Retrieve a specific curriculum pack by board code and grade."""
    try:
        return curriculum_service.load_pack(board=board, grade=grade)
    except CurriculumPackNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Curriculum pack not found for board '{board}' and grade {grade}.",
        )


@router.get("/topics/{board}/{grade}", response_model=list[TopicConfig])
@limiter.limit("60/minute")
def get_topics_for_board_and_grade(
    request: Request,
    board: str,
    grade: int,
) -> list[TopicConfig]:
    """Retrieve the topics list for a specific board and grade."""
    try:
        pack = curriculum_service.load_pack(board=board, grade=grade)
        return pack.topics
    except CurriculumPackNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Topics not found for board '{board}' and grade {grade}.",
        )
