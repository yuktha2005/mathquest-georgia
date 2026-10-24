"""Curriculum Pack Loader and Registry Service.

Loads, validates, caches, and queries curriculum packs from backend/data/packs/.
Enforces multi-curriculum extensibility: expanding boards requires adding data files,
never changing application code.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.schemas import CurriculumPack, Tier, TierRule, TopicConfig

logger = logging.getLogger(__name__)


class CurriculumPackNotFoundError(Exception):
    """Raised when a requested curriculum pack (board, grade) cannot be found on disk."""
    pass


class CurriculumPackService:
    """Service for managing and querying curriculum packs."""

    def __init__(self, packs_dir: Path | None = None) -> None:
        if packs_dir is None:
            # Default to backend/data/packs relative to this file
            self.packs_dir = Path(__file__).resolve().parent.parent.parent / "data" / "packs"
        else:
            self.packs_dir = packs_dir
        self._cache: dict[tuple[str, int], CurriculumPack] = {}

    def get_pack_path(self, board: str, grade: int) -> Path:
        """Construct the standard file path for a curriculum pack."""
        norm_board = board.strip().lower()
        return self.packs_dir / f"{norm_board}-g{grade}.json"

    def load_pack(self, board: str, grade: int, use_cache: bool = True) -> CurriculumPack:
        """Load and strictly validate a curriculum pack from disk.

        Args:
            board: Curriculum board code, e.g. 'georgia', 'cbse'
            grade: Target grade level, e.g. 5 or 6
            use_cache: Whether to return cached pack if already loaded

        Raises:
            CurriculumPackNotFoundError: If no matching pack JSON file exists.
            ValidationError: If the JSON file violates CurriculumPack Pydantic schema.
        """
        norm_board = board.strip().lower()
        cache_key = (norm_board, grade)

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        pack_file = self.get_pack_path(norm_board, grade)
        if not pack_file.exists():
            raise CurriculumPackNotFoundError(
                f"Curriculum pack for board='{norm_board}', grade={grade} not found at {pack_file}."
            )

        try:
            with open(pack_file, "r", encoding="utf-8") as f:
                content = f.read()
            pack = CurriculumPack.model_validate_json(content)
            self._cache[cache_key] = pack
            logger.info("Loaded curriculum pack: %s Grade %d (%d topics)", pack.board_name, pack.grade, len(pack.topics))
            return pack
        except Exception as e:
            logger.error("Failed to load or validate curriculum pack %s: %s", pack_file, e)
            raise

    def list_packs(self) -> list[CurriculumPack]:
        """Scan the packs directory and load all valid curriculum packs."""
        packs: list[CurriculumPack] = []
        if not self.packs_dir.exists():
            return packs

        for file_path in sorted(self.packs_dir.glob("*-g*.json")):
            try:
                # Extract board and grade from filename: e.g. 'georgia-g5.json'
                stem = file_path.stem
                if "-g" in stem:
                    parts = stem.split("-g")
                    board = parts[0]
                    grade = int(parts[1])
                    pack = self.load_pack(board, grade)
                    packs.append(pack)
            except Exception as e:
                logger.warning("Skipping invalid pack file %s: %s", file_path, e)
        return packs

    def get_topic_config(self, board: str, grade: int, topic_id: str) -> TopicConfig | None:
        """Retrieve the TopicConfig for a given board, grade, and topic."""
        try:
            pack = self.load_pack(board, grade)
            return pack.get_topic(topic_id)
        except CurriculumPackNotFoundError:
            return None

    def get_tier_rule(
        self,
        board: str,
        grade: int,
        topic_id: str,
        tier: Tier | str,
    ) -> TierRule | None:
        """Retrieve the TierRule for a specific tier in a topic."""
        topic = self.get_topic_config(board, grade, topic_id)
        if not topic:
            return None
        tier_key = tier.value if isinstance(tier, Tier) else str(tier).lower().strip()
        return topic.tier_rules.get(tier_key)

    def clear_cache(self) -> None:
        """Clear the in-memory pack cache."""
        self._cache.clear()


# Global singleton instance
curriculum_service = CurriculumPackService()


def get_curriculum_pack(board: str, grade: int) -> CurriculumPack:
    """Convenience helper to retrieve a curriculum pack."""
    return curriculum_service.load_pack(board, grade)


def list_curriculum_packs() -> list[CurriculumPack]:
    """Convenience helper to list all available curriculum packs."""
    return curriculum_service.list_packs()


def get_topic_config(board: str, grade: int, topic_id: str) -> TopicConfig | None:
    """Convenience helper to retrieve topic config."""
    return curriculum_service.get_topic_config(board, grade, topic_id)
