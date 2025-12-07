# src/core/heuristic_estimator.py
import re

from typing import Any, Dict, List, Tuple
from tabulate import tabulate

from utils.yml_parser import yml_load_keywords

from config.app_settings import DEF_TABLE_FMT
from config.log.logger import setup_logger


WORD_COUNT_THRESHOLD = 12
WORD_COUNT_BONUS = 15

logger = setup_logger(__name__)


class HeuristicEstimator:
    """
    Heuristic estimator based on a keyword → minutes mapping.
    Includes contextual logging for debugging, observability, and auditing.
    """

    def __init__(self, keyword_table: Dict[str, int] | None = None):
        logger.debug("Initializing HeuristicEstimator...")

        try:
            self.keywords: Dict[str, int] = keyword_table or yml_load_keywords() or {}
        except Exception as e:
            logger.error(f"Failed to load keywords from YAML: {e}")
            raise

        if not self.keywords:
            logger.error(
                "Keyword table is empty — heuristic estimation will be ineffective."
            )

        logger.info(f"Loaded {len(self.keywords)} heuristic keywords.")

        # Compile pattern
        try:
            keys_sorted = sorted(self.keywords.keys(), key=len, reverse=True)
            if keys_sorted:
                pattern = r"\b(" + "|".join(map(re.escape, keys_sorted)) + r")\b"
                self._pattern = re.compile(pattern, flags=re.IGNORECASE)
                logger.debug(f"Compiled keyword regex with {len(keys_sorted)} entries.")
            else:
                self._pattern = re.compile(r"(?!x)x")
                logger.warning("No keywords found — compiled a dummy regex.")

        except Exception as e:
            logger.error(f"Regex compilation failed: {e}")
            raise

    # -------------------------------------------------------------------------
    def _text_scores(self, text: str) -> Tuple[int, List[str], int]:
        logger.debug("Starting heuristic text scoring...")

        text = (text or "").strip().lower()
        if not text:
            logger.warning("Received empty text for scoring.")

        wc = len(text.split())
        logger.debug(f"Word count: {wc}")

        # Match keywords
        try:
            matches_raw = self._pattern.findall(text)
        except Exception as e:
            logger.error(f"Regex error while matching text: {e}")
            matches_raw = []

        matches = []
        for m in matches_raw:
            ml = m.lower()
            if ml not in matches:
                matches.append(ml)

        logger.debug(f"Matched keywords: {matches}")

        # Scoring strategy — keeping current MAX model
        if matches:
            score_kw = max(self.keywords.get(m, 0) for m in matches)
            logger.debug(f"Keyword-derived score (max strategy): {score_kw}")
        else:
            logger.info("No heuristic keywords matched in text.")
            score_kw = 0

        # Word-count bonus
        if wc >= WORD_COUNT_THRESHOLD:
            logger.info(
                f"Applying word count bonus ({WORD_COUNT_BONUS}) due to long task text."
            )
            score_kw += WORD_COUNT_BONUS

        logger.debug(f"Final score after heuristics: {score_kw}")

        return int(score_kw), matches, wc

    # -------------------------------------------------------------------------
    def estimate(self, task: object) -> Dict[str, Any]:
        """
        Returns structured heuristic estimation for a task.
        Logging includes context-aware information when possible.
        """

        ctx = f"(task_id={task.id})" if task.id else ""

        logger.info(f"Running heuristic estimation {ctx}...")

        # Extract text sources
        if isinstance(task, dict):
            content = task.content or ""
            description = task.description or ""
        else:
            content = getattr(task, "content", "") or ""
            description = getattr(task, "description", "") or ""

        if not content and not description:
            logger.warning(f"No content/description found {ctx}. Returning no_match=0.")

        text_combined = f"{content} {description}".strip().lower()
        logger.debug(f"Combined text for heuristic evaluation {ctx}: {text_combined}")

        score, matches, wc = self._text_scores(text_combined)

        reason = "heuristic" if score > 0 else "no_match"
        logger.info(
            f"Heuristic estimation completed {ctx} → score={score}, reason={reason}"
        )

        return {
            "estimated_mins": score,
            "reason": reason,
            "matches": matches,
            "word_count": wc,
        }

    # -------------------------------------------------------------------------
    @staticmethod
    def estimation_totable(estimation_result: Dict[str, Any]) -> str:
        """
        Returns structured heuristic estimation for a task formatted as a tabulate table.
        """
        
        # Convert to list of rows: [(key, value), ...]
        rows = [(k, v) for k, v in estimation_result.items()]
        headers = ["Field", "Value"]

        return tabulate(rows, headers=headers, tablefmt=DEF_TABLE_FMT)
