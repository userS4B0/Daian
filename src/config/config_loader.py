import os
import yaml
from copy import deepcopy
from typing import Dict, Any

from config.log.logger import setup_logger

logger = setup_logger(__name__)


class ConfigLoader:
    """
    Loads DAIAN configuration following priority:

    1. DAIAN_CONFIG_DIR override (developer)
    2. User config (~/.config/daian)
    3. System config (/etc/daian)
    4. Defaults shipped in the package (src/config)

    Merge order:
        defaults ← system ← user ← override
    """

    USER_CONFIG_DIR = os.path.expanduser("~/.config/daian/")
    SYSTEM_CONFIG_DIR = "/etc/daian/"
    DEFAULT_CONFIG_DIR = os.path.join(os.path.dirname(__file__))

    _cache: Dict[str, Any] = {}

    # ---------------------- Deep Merge -----------------------------------
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

    # ---------------------- YAML Loader -----------------------------------
    # FIXME: Properly export function to utils/yml_utils
    # Export _load_yaml class function to utils/yml_utils & use load_yml function
    # assignees: userS4B0
    # labels: priority_medium, core, bug
    # milestone: v1.0.0
    @staticmethod
    def _load_yaml(filepath: str) -> Dict[str, Any]:
        """Loads YAML safely or returns {}."""
        if not os.path.exists(filepath):
            return {}

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                logger.debug(f"Loaded config: {filepath}")
                return data
        except Exception as e:
            logger.error(f"Failed to load YAML at {filepath}: {e}")
            return {}

    # ----------------------- Priority Resolution ---------------------------
    @classmethod
    def _get_candidate_dirs(cls) -> list[str]:
        """Return config directories in correct priority order."""
        dirs = []

        # Manual override for developers
        override_dir = os.getenv("DAIAN_CONFIG_DIR")
        if override_dir:
            override_dir = os.path.abspath(override_dir)
            logger.debug(f"Using DAIAN_CONFIG_DIR override: {override_dir}")
            dirs.append(override_dir)

        # User config
        dirs.append(cls.USER_CONFIG_DIR)

        # System config
        dirs.append(cls.SYSTEM_CONFIG_DIR)

        # Defaults (shipped-in config)
        dirs.append(cls.DEFAULT_CONFIG_DIR)

        return dirs

    # --------------------- Public API -------------------------------------
    @classmethod
    def load(cls, name: str) -> Dict[str, Any]:
        """
        Load <name>.yaml from ALL config levels respecting priority:
        override > user > system > defaults.
        """
        if name in cls._cache:
            return cls._cache[name]

        filename = f"{name}.yaml"

        merged: Dict[str, Any] = {}

        # Resolve all directories in order
        for directory in cls._get_candidate_dirs():
            filepath = os.path.join(directory, filename)
            data = cls._load_yaml(filepath)

            if data:
                logger.debug(f"Merging config from: {filepath}")
                merged = cls._deep_merge(merged, data)

        cls._cache[name] = merged
        return merged
