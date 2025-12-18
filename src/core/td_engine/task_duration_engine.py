from typing import Dict, Any, Optional

from core.td_engine.heuristic_estimator import HeuristicEstimator
from core.td_engine.history_store import HistoryStore

from config.log.logger import setup_logger

from utils.str_utils import generate_datatable

logger = setup_logger(__name__)


class TaskDurationEngine:
    """
    Hybrid duration engine:
      1) baseline rules (priority, simple length rules)
      2) heuristic estimator (keyword + length)
      3) historical averages (per-key)
    Combines them with a simple strategy:
      - If history exists for a matched keyword, prefer history.
      - Otherwise combine max(baseline, heuristic) and round.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.td_engine_cfg = config.get("td_engine", {})  # Instanciate specific config

        self.heuristic = HeuristicEstimator(config)
        self.history = HistoryStore(self.td_engine_cfg.get("history_path", ""))

        # Baseline defaults
        self.priority_mapper = self.td_engine_cfg.get(
            "priority_mapper", {"p4": 90, "p3": 60, "p2": 30, "p1": 15}
        )
        self.task_lenght_heur = self.td_engine_cfg.get("task_length_heur", 15)
        self.task_lenght_inc = self.td_engine_cfg.get("task_length_inc", 15)
        self.quick_lbl_inc = self.td_engine_cfg.get("quick_lbl_inc", 15)
        self.deepwork_lbl_inc = self.td_engine_cfg.get("deepwork_lbl_inc", 60)

    def _normalize_key(self, key: str) -> str:
        return "_".join(key.strip().lower().split())

    def _derive_history_key(self, task: object) -> Optional[str]:
        """
        Derive a stable, descriptive history key.
        Avoid single-token generic keys (e.g. 'itv').
        """
        content = task.content.lower().strip() if task.content else ""
        tokens = content.split()

        if not tokens:
            return None

        # Try heuristic matches ONLY if they are descriptive (>= 2 tokens)
        heur = self.heuristic.estimate(task) or {}
        matches = heur.get("matches", [])

        if matches:
            match = matches[0].strip().lower()
            if len(match.split()) >= 2:
                return self._normalize_key(match)

        # Fallback: first 3 tokens from content
        key_tokens = tokens[:3]

        return self._normalize_key("_".join(key_tokens))

    def _baseline_estimate(self, task: object) -> int:
        # Basic baseline mapping by priority (Todoist-style 1..4)
        # Assumes high number means more important

        base = self.priority_mapper.get(f"p{task.priority}", 30)
        logger.info(
            f"Baseline estimator got a match on {task.id} | reason: task_priority initial estimation: {base} mins"
        )

        # Task Lenght Estimation
        task_content = task.content.lower().split() or ""

        if len(task_content) > self.task_lenght_heur:
            logger.info(
                f"Baseline estimator got a match on {task.id} | reason: task_lenght"
            )
            base += self.task_lenght_inc

        # Label based Estimation
        task_labels = task.labels or []

        # FIXME: Add real todoist labels parsed by yaml config on _baseline_estimate func
        # Parse config data instead of hardcoding label names
        # assignees: userS4B0
        # labels: priority_low, td_engine, bug
        # milestone: v1.0.0
        if "Quick" in task_labels:
            logger.info(
                f"Baseline estimator got a match on {task.id} | reason: `quick_lbl` found"
            )
            base = min(base, self.quick_lbl_inc)
        if "DeepWork" in task_labels:
            logger.info(
                f"Baseline estimator got a match on {task.id} | reason: `deepwork_lbl` found"
            )
            base = max(base, self.deepwork_lbl_inc)

        return base

    def estimate(self, task: object) -> Dict[str, Any]:
        """
        Returns:
            {
              'estimated_minutes': int,
              'components': {
                 'baseline': int,
                 'heuristic': int,
                 'history': Optional[float]
              },
              'reason': str
            }
        """
        baseline = self._baseline_estimate(task) or 0

        heur = self.heuristic.estimate(task) or 0
        heur_mins = int(heur.get("estimated_minutes", 0))

        # Derive History Key
        history_key = self._derive_history_key(task)
        history_avg = None
        estimated_mins = max(baseline, heur_mins)
        reason = "baseline" if heur_mins == 0 else "heuristic+baseline"

        if history_key:
            history_avg = self.history.get_avg_minutes(history_key)

            if history_avg is not None:
                stat = self.history.get(history_key, {"count": 1})
                count = stat.get("count", 1)

                if count >= 5:
                    estimated_mins = round(history_avg)
                    reason = f"history: {history_key}"

                else:
                    estimated_mins = round((history_avg + max(baseline, heur_mins)) / 2)
                    reason = f"blend:history:{history_key}"

        else:
            estimated_mins = max(baseline, heur_mins)
            reason = "baseline" if heur_mins == 0 else "heuristic+baseline"

        return {
            "task_id": task.id,
            "task_content": task.content,
            "estimated_minutes": int(estimated_mins),
            "components": {
                "baseline": int(baseline),
                "heuristic": int(heur_mins),
                "history": float(history_avg) if history_avg is not None else None,
            },
            "reason": reason,
            "history_key": history_key,
        }

    def record_actual_duration(self, task: object, actual_minutes: int, source: str) -> None:
        """
        Register real duration for historical learning.
        """
        history_key = self._derive_history_key(task)
        if not history_key:
            logger.warning("No hisotry key derived, skipping learning")

        self.history.add_sample(history_key, actual_minutes, source)
        logger.info(f"[Daian Learn] New entry learned: key={history_key} minutes={actual_minutes}")

    # -------------------------------------------------------------------------
    @staticmethod
    def estimation_totable(estimation_result: Dict[str, Any]) -> str:
        """
        Returns structured estimation for a task formatted as a tabulate table.
        """

        # Convert to list of rows: [(key, value), ...]
        estimation_data = [(key, value) for key, value in estimation_result.items()]
        estimation_headers = ["Analyzed Field", "Value"]

        return generate_datatable(estimation_data, estimation_headers)