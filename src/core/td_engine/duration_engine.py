from typing import Dict, Any, Object

from core.td_engine.heuristic_estimator import HeuristicEstimator
from core.td_engine.history_store import HistoryStore

from config.log.logger import setup_logger

logger = setup_logger(__name__)


class DurationEngine:
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
        self.history = HistoryStore(self.td_engine_cfg.get("history_path", {}))

        # Baseline defaults
        self.priority_mapper = self.td_engine_cfg.get(
            "priority_mapper", {"p4": 90, "p3": 60, "p2": 30, "p1": 15}
        )
        self.task_lenght_heur = self.td_engine_cfg.get("task_length_heur", 15)
        self.task_lenght_inc = self.td_engine_cfg.get("task_length_inc", 15)
        self.quick_lbl_inc = self.td_engine_cfg.get("quick_lbl_inc", 15)
        self.deepwork_lbl_inc = self.td_engine_cfg.get("deepwork_lbl_inc", 60)

    def baseline_estimate(self, task: Object) -> int:
        # Basic baseline mapping by priority (Todoist-style 1..4)
        # Assumes high number means more important

        base = self.priority_mapper.get(f"p{task.priority}", 30)

        # Lenght Heuristic
        task_content = task.content.lower().split() or ""

        if len(task_content) > self.task_lenght_heur:
            base += self.task_lenght_inc

        # Label based Heuristic
        task_labels = task.labels or []

        # Implement this in todoist client & add methods to get this config parameters
        if "quick" in task_labels:
            base = min(base, self.quick_lbl_inc)
        if "deepwork" in task_labels:
            base = max(base, self.deepwork_lbl_inc)

    def estimate(self, task: Object) -> Dict[str, Any]:
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
        baseline = self.baseline_estimate(task)
        heur = self.heuristic.estimate(task)
        heur_mins = int(heur.get("estimated_minutes", 0))

        # History Key Derivation
        history_key = heur.get("matches", [])
        if history_key:
            history_key = history_key[0]
        else:
            content = task.content.strip().lower() or ""
            tokens = content.split()
            history_key = " ".join(tokens[:2]) if tokens else None

        history_avg = None
        if history_key:
            history_avg = self.history.get_avg_minutes(history_key)

        history_avg = self.history.get_avg_minutes(history_key) if history_key else None

        if history_avg:
            stat = self.history.get(history_key, {"count": 1})
            count = stat.get("count", 1)
            if count >= 5:
                estimated_mins = round(history_avg)
                reason = f"history:{history_key}"
            else:
                estimated_mins = round((history_avg + max(baseline, heur_mins)) / 2)
                reason = f"blend:history:{history_key}"
        else:
            estimated_mins = max(baseline, heur_mins)
            reason = "baseline" if heur_mins == 0 else "heuristic+baseline"

        return {
            "estimated_minutes": int(estimated_mins),
            "components": {
                "baseline": int(baseline),
                "heuristic": int(heur_mins),
                "history": float(history_avg) if history_avg else None,
            },
            "reason": reason,
        }

    def register_actual(self, task: Object, actual_minutes: float):
        """
        After task completion (or by aligning scheduled event with real duration),
        register the actual minutes for the derived key.
        """
        # same history key derivation logic
        heur = self.heuristic.estimate(task)
        history_key = heur.get("matches", [])
        if history_key:
            history_key = history_key[0]
        else:
            content = task.content.strip().lower() or ""
            tokens = content.split()
            history_key = " ".join(tokens[:2]) if tokens else None

        if history_key:
            self.history.update(history_key, actual_minutes)
