import os
import yaml

from copy import deepcopy
from typing import Dict, Any

from config.log.logger import setup_logger

logger = setup_logger(__name__)


class ConfigLoader:
    """
    Loads DAIAN configuration following the priority:
    1) User config:     ~/.config/daian/*.yaml
    2) System config:   /etc/daian/*.yaml
    3) Defaults:        src/config/*.yaml
    Merges them in order with deep override.
    """

    USER_CONFIG_DIR = os.path.expanduser("~/.config/daian/")
    SYSTEM_CONFIG_DIR = "/etc/daian/"
    DEFAULT_CONFIG_DIR = os.path.join(
        os.path.dirname(__file__)
    )  # src/config/

    _cache: Dict[str, Any] = {}

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Deep merge override → base."""
        result = deepcopy(base)
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)
        return result

    @staticmethod
    def _load_yaml(filepath: str) -> Dict[str, Any]:
        """Loads YAML or returns {} if file not found."""
        if not os.path.exists(filepath):
            return {}

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                logger.debug(f"Loaded config file: {filepath}")
                return data
        except Exception as e:
            logger.error(f"Failed to load YAML: {filepath} → {e}")
            return {}

    @classmethod
    def load(cls, name: str) -> Dict[str, Any]:
        """
        Loads <name>.yaml from all 3 levels with priority:
        user > system > defaults.
        """
        if name in cls._cache:
            return cls._cache[name]

        filename = f"{name}.yaml"

        # 1) Load defaults
        default_path = os.path.join(cls.DEFAULT_CONFIG_DIR, filename)
        defaults = cls._load_yaml(default_path)

        # 2) Load system
        system_path = os.path.join(cls.SYSTEM_CONFIG_DIR, filename)
        system_conf = cls._load_yaml(system_path)

        # 3) Load user
        user_path = os.path.join(cls.USER_CONFIG_DIR, filename)
        user_conf = cls._load_yaml(user_path)

        # Merge: defaults ← system ← user
        merged = cls._deep_merge(defaults, system_conf)
        merged = cls._deep_merge(merged, user_conf)

        cls._cache[name] = merged
        return merged
