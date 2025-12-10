import json

from pathlib import Path
from typing import Optional, Dict


class HistoryStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else Path("data/task_history.json")
        self._data: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    self._data = json.load(f)

            except Exception:
                self._data = {}  # If corrupted, start fresh to avoid crashes

        else:
            self._data = {}

    def _save(self):
        try:
            with self.path.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)

        except Exception:
            pass  # Do not raise on disk write failures

    def get(self, key: str) -> Optional[Dict]:
        """Return stored stat for key or None."""
        return self.data.get(key)

    def get_avg_minutes(self, key: str) -> Optional[float]:
        stat = self.get(key)

        return stat.get("avg") if stat else None

    def update(self, key: str, minutes: float):
        """Update the running average for a key."""
        stat = self.data.get(key)

        if stat:
            total = stat.get("avg", 0.0) * stat.get("count", 0)
            total += minutes
            stat["count"] += 1
            stat["avg"] = total / stat["count"]

        else:
            self._data[key] = {"avg": float(minutes), "count": 1}
        self._save()
