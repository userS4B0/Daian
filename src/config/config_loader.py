import os
from copy import deepcopy
from typing import Dict, Any

from config.validator import ConfigValidator
from utils.yaml_parser import load_yaml

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
        """Deep merge override > base."""
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

    # ----------------------- Priority Resolution ---------------------------
    @classmethod
    def _get_candidate_dirs(cls) -> list[str]:
        """Return config directories in correct priority order."""
        dirs = []

        # Developer Override
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

    # --------------------- Load specific config file -----------------------
    @classmethod
    def load(cls, name: str) -> Dict[str, Any]:
        """
        Load <name>.yaml across all levels.
        """
        if name in cls._cache:
            return cls._cache[name]

        filename = f"{name}.yaml"

        merged: Dict[str, Any] = {}

        # Resolve all directories in order
        for directory in cls._get_candidate_dirs():
            filepath = os.path.join(directory, filename)
            data = load_yaml(filepath)

            if data:
                logger.debug(f"Merging config from: {filepath}")
                merged = cls._deep_merge(merged, data)

        cls._cache[name] = merged
        return merged

    # --------------------- Load all config files ---------------------------
    @classmethod
    def load_all(cls) -> Dict[str, Any]:
        """
        Load all known config files and perform full merge.
        """
        merged = cls._deep_merge(cls.load("app_settings"), cls.load("user_settings"))
        return merged

    # --------------------- Apply logger config ------------------------------
    @staticmethod
    def _apply_logger_settings(config: Dict[str, Any]):
        """
        Update logger_config module dynamically using loaded YAML config.
        """
        try:
            from config.log import logger_config

            logging_cfg = config.get("app", {}).get("log", {})

            path = logging_cfg.get("log_file_path")
            console = logging_cfg.get("console_level")
            file_lvl = logging_cfg.get("file_level")

            if path:
                logger_config.LOG_FILE_PATH = path

            if console:
                logger_config.CONSOLE_LEVEL = console.upper()

            if file_lvl:
                logger_config.FILE_LEVEL = file_lvl.upper()

            logger.info(
                f"Logger configuration applied: "
                f"path={logger_config.LOG_FILE_PATH}, "
                f"console={logger_config.CONSOLE_LEVEL}, "
                f"file={logger_config.FILE_LEVEL}"
            )

        except Exception as e:
            logger.error(f"Failed to apply logger settings: {e}")

    # --------------------- Public API -------------------------------------
    @classmethod
    def load_and_validate(cls) -> Dict[str, Any]:
        """Load all configuration, validate it, and apply logger settings."""
        config = cls.load_all()

        # Validate structure
        if not ConfigValidator.validate(config):
            raise RuntimeError("DAIAN configuration missing required fields.")

        # Apply dynamic logger config (NO circular dependency)
        cls._apply_logger_settings(config)

        return config
