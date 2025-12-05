# src/core/duration_engine.py
from typing import Optional

from core.heuristic_estimator import HeuristicEstimator
from core.history_store import HistoryStore

# from client.todoist_client import process_task_content

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

    def __init__(self, history_path: Optional[str] = None):
        self.heuristic = HeuristicEstimator()
        self.history = HistoryStore(history_path)

    def baseline_estimate(self, task: list[object]) -> int:
        # Basic baseline mapping by priority (Todoist-style 1..4)
        # Assumes high number means more important; adjust as your system defines
        pr = task.priority
        mapping = {4: 90, 3: 60, 2: 30, 1: 15}
        base = mapping.get(pr, 30)

        # length heuristic (long content -> +15)
        content = (task.content or "")
        if len(content.split()) > 15:
            base += 15

        # tags that adjust durations (example)
        labels = task.labels or [str]
        if isinstance(labels, (list, tuple)) and "quick" in labels:
            base = min(base, 15)
        if "deepwork" in labels:
            base = max(base, 60)

        return int(base)

    def estimate(self, task: list[object]) -> dict[str, any]:
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
        heur_minutes = int(heur.get("estimated_minutes", 0))

        # try to derive a history key: prefer a heuristic match keyword if present,
        # fallback to normalized short content token.
        history_key = None
        if heur.get("matches"):
            # pick first match as key
            history_key = heur["matches"][0]
        else:
            # use first two words of content as a key (simple clustering)
            content = (task.content or "").strip().lower()
            tokens = content.split()
            if tokens:
                history_key = " ".join(tokens[:2])

        history_avg = None
        if history_key:
            history_avg = self.history.get_avg_minutes(history_key)

        # If we have history for this key, use a weighted average between history and baseline/heuristic
        if history_avg:
            # weight history heavily if count is significant (we already stored count in history)
            stat = self.history.get(history_key)
            count = stat.get("count", 1)
            # simple weighting: if count >= 5 prefer history, otherwise blend
            if count >= 5:
                est = round(history_avg)
                reason = f"history:{history_key}"
            else:
                # blend: average of history and max(baseline,heur)
                est = round((history_avg + max(baseline, heur_minutes)) / 2)
                reason = f"blend:history:{history_key}"
        else:
            # no history: use max(baseline, heuristic)
            est = max(baseline, heur_minutes)
            # if heuristic produced 0, fallback to baseline
            reason = "baseline" if heur_minutes == 0 else "heuristic+baseline"

        return {
            "estimated_minutes": int(est),
            "components": {
                "baseline": int(baseline),
                "heuristic": int(heur_minutes),
                "history": float(history_avg) if history_avg else None,
            },
            "reason": reason,
        }

    def register_actual(self, task: list[object], actual_minutes: float):
        """
        After task completion (or by aligning scheduled event with real duration),
        register the actual minutes for the derived key.
        """
        # same history key derivation logic
        heur = self.heuristic.estimate(task)
        history_key = None
        if heur.get("matches"):
            history_key = heur["matches"][0]
        else:
            content = (task.content or "").strip().lower()
            tokens = content.split()
            if tokens:
                history_key = " ".join(tokens[:2])
        if history_key:
            self.history.update(history_key, actual_minutes)
