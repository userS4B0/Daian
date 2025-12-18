import json

from typing import Optional, Dict, Any
from pathlib import Path

from config.log.logger import setup_logger

from utils import time_utils

logger = setup_logger(__name__)


class HistoryStore:
    def __init__(self, path: Optional[str] = None):
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

    def get(self, key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Return stored stat for key or default if not present.
        """
        return self._data.get(key, default)

    def get_avg_minutes(self, key: str) -> Optional[float]:
        stat = self.get(key)

        return stat.get("avg_minutes") if stat else None

    def add_sample(self, key: str, minutes: float, source: str = "unknown") -> None:
        """
        Register a real task duration sample for learning purposes.
        """

        if not key:
            logger.warning(
                "Tried to add new learning sample with empty key, skipping learning"
            )
            return

        if minutes <= 0:
            logger.warning(
                f"Tried to add new learning sample with non-positive minutes ({minutes}) for key={key}, skipping learning"
            )
            return

        stat = self._data.get(key)

        if not stat:
            stat = {
                "count": 0,
                "total_minutes": 0.0,
                "avg_minutes": 0.0,
                "samples": [],
            }
            self._data[key] = stat

        # Update stats
        stat["count"] += 1
        stat["total_minutes"] += float(minutes)
        stat["avg_minutes"] = stat["total_minutes"] / stat["count"]

        # Keep samples bounded (prevent file explosion)
        stat.setdefault("samples", []).append(float(minutes))
        if len(stat["samples"]) > 20:
            stat["samples"].pop(0)

        last_updated = str(time_utils.get_today())
        stat["last_source"] = source
        stat["last_updated"] = last_updated

        logger.info(
            f"Learning recorded: key={key}, minutes={minutes}, avg={stat['avg_minutes']:.1f}"
        )

        self._save()
