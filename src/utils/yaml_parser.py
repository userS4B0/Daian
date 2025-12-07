import os
import yaml

from typing import Dict

from config.log.logger import setup_logger

logger = setup_logger(__name__)

# Caching system so it doesn't load always from disk
_KEYWORDS_CACHE = None


def yaml_load_keywords() -> Dict:
    """Load keyword → weight mapping from data/keywords.yml."""

    global _KEYWORDS_CACHE

    # If it's loaded, reuse
    if _KEYWORDS_CACHE is not None:
        return _KEYWORDS_CACHE

    # Absolute path to project src/ 
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Path to /data/keywords.yml
    file_path = os.path.join(project_root, "data", "keywords.yml")

    if not os.path.exists(file_path):
        logger.error(f"Keywords file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        _KEYWORDS_CACHE = yaml.safe_load(f) or {}

    return _KEYWORDS_CACHE
