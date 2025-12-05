import json

from pathlib import Path

from config.app_settings import DEF_TASK_HISTORY_STORE_PATH
from typing import Optional

class HistoryStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else Path(DEF_TASK_HISTORY_STORE_PATH)
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                # If corrupted, start fresh to avoid crashes
                self._data = {}
        else:
            self._data = {}

    def _save(self):
        try:
            with self.path.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            # Best-effort: do not raise on disk write failures
            pass

    def get(self, key: str) -> Optional[dict]:
        """Return stored stat for key or None."""
        return self._data.get(key)

    def get_avg_minutes(self, key: str) -> Optional[float]:
        stat = self.get(key)
        if stat:
            return stat.get("avg")
        return None

    def update(self, key: str, minutes: float):
        """Update the running average for a key."""
        stat = self._data.get(key)
        if stat:
            # Weighted moving average simple update
            total = stat.get("avg", 0.0) * stat.get("count", 0)
            total += minutes
            stat["count"] = stat.get("count", 0) + 1
            stat["avg"] = total / stat["count"]
        else:
            self._data[key] = {"avg": float(minutes), "count": 1}
        self._save()