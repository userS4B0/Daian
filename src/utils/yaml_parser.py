import os
import yaml

from typing import Dict, Any
from pathlib import Path

from config.log.logger import setup_logger

logger = setup_logger(__name__)

# Caching system so it doesn't load always from disk
_KEYWORDS_CACHE = None

# ---------------------- YAML Loader -----------------------------------
def load_yaml(filepath: str) -> Dict[str, Any]:
    """Loads YAML safely or returns {}."""
    if not os.path.exists(filepath):

        logger.warning(f"Path {filepath} does not exist")
        
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
def yaml_load_keywords(config: Dict[str, Any] = None) -> Dict:
    """Load keyword → weight mapping from data/keywords.yml."""

    global _KEYWORDS_CACHE

    # If it's loaded, reuse
    if _KEYWORDS_CACHE is not None:
        logger.debug("Keyword file already in cache, reusing...")
        return _KEYWORDS_CACHE
    
    # Path to /data/keywords.yml
    logger.debug("Loading keywords from config")
    
    keywords_path = Path(config.get("keywords_path", ""))

    logger.info(f"Keywords file found at {keywords_path}")

    _KEYWORDS_CACHE = load_yaml(keywords_path)

    return _KEYWORDS_CACHE
