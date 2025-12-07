import os
import yaml

from typing import Dict, Any

from config.log.logger import setup_logger

logger = setup_logger(__name__)

# Caching system so it doesn't load always from disk
_KEYWORDS_CACHE = None

# ---------------------- YAML Loader -----------------------------------
def load_yaml(filepath: str) -> Dict[str, Any]:
    """Loads YAML safely or returns {}."""
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            logger.debug(f"Loaded file: {filepath}")
            return data
    except Exception as e:
        logger.error(f"Failed to load YAML at {filepath}: {e}")
        return {}

# ---------------------- YAML Load Keywords ----------------------------
def yaml_load_keywords() -> Dict:
    """Load keyword → weight mapping from data/keywords.yml."""

    global _KEYWORDS_CACHE

    # If it's loaded, reuse
    if _KEYWORDS_CACHE is not None:
        logger.debug("Keyword file already in cache, reusing...")
        return _KEYWORDS_CACHE

    # Absolute path to project src/ 
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Path to /data/keywords.yml
    keywords_path = os.path.join(project_root, "data", "keywords.yaml")

    _KEYWORDS_CACHE = load_yaml(keywords_path)

    return _KEYWORDS_CACHE
