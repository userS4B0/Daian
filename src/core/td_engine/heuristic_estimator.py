# src/core/heuristic_estimator.py
import re

from typing import Any, Dict, List, Tuple

from config.log.logger import setup_logger

from utils.yaml_parser import yaml_load_keywords
from utils.str_utils import generate_datatable


logger = setup_logger(__name__)


class HeuristicEstimator:
    """
    Heuristic estimator based on a keyword → minutes mapping.
    Includes contextual logging for debugging, observability, and auditing.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.td_engine_cfg = config.get("td_engine", {})  # Instanciate specific config

        self.word_count_threshold = self.td_engine_cfg.get("word_count_threshold", 12)
        self.word_count_bonus = self.td_engine_cfg.get("word_count_bonus", 15)

        # keywords_path = self.td_engine_cfg.get("keywords_path", "")
        # self.keywords = yaml_load_keywords(keywords_path) if keywords_path else {}
        self.keywords = yaml_load_keywords()

        keys_sorted = sorted(self.keywords.keys(), key=len, reverse=True)

        self.pattern = (
            re.compile(
                r"\b(" + "|".join(map(re.escape, keys_sorted)) + r")\b", re.IGNORECASE
            )
            if keys_sorted
            else re.compile(r"(?!x)x")
        )

    # -------------------------------------------------------------------------
    def _text_scores(self, text: str) -> Tuple[int, List[str], int]:
        text = (text or "").strip().lower()
        wc = len(text.split())

        matches_raw = self.pattern.findall(text) if text else []

        matches = []

        for m in matches_raw:
            ml = m.lower()
            if ml not in matches:
                matches.append(ml)

        score_kw = max([self.keywords.get(m, 0) for m in matches], default=0)

        if wc >= self.word_count_threshold:
            score_kw += self.word_count_bonus

        return int(score_kw), matches, wc

    # -------------------------------------------------------------------------
    def estimate(self, task: object) -> Dict[str, Any]:
        """
        Returns structured heuristic estimation for a task.
        Logging includes context-aware information when possible.
        """

        content = task.content or ""
        description = task.description or ""
        text_combined = f"{content} {description}".strip().lower()

        score, matches, wc = self._text_scores(text_combined)

        reason = "heuristic" if score > 0 else "no_match"
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
        estimation_data = [(key, value) for key, value in estimation_result.items()]
        estimation_headers = ["Analyzed Field", "Value"]

        return generate_datatable(estimation_data, estimation_headers)
