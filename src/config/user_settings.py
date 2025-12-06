import os
from dotenv import load_dotenv

from config.log.logger import setup_logger

logger = setup_logger(__name__)

# Load environment variables from .env file
logger.debug("Loading user settings")
try:
    load_dotenv()

    # ----- Google calendar IDs (defined on .env) --------------------------
    GCAL_ID_TASKS = os.getenv("GCAL_ID_TASKS")
    GCAL_ID_WORK = os.getenv("GCAL_ID_WORK")
    GCAL_ID_TIMEMANAGE = os.getenv("GCAL_ID_TIMEMANAGE")
    GCAL_ID_PERSONALEVENTS = os.getenv("GCAL_ID_PERSONALEVENTS")

    # ----- Default user timezone (defined on .env) ------------------------
    DEF_TZ = os.getenv("DEF_TZ")

except Exception as e:
    logger.error(f"Error loading user settings: {e}")

# ----- Default label for non-scheduled tasks --------------------------
NONSCHEDULED_TASKS_LABEL = "Agendar"

# ----- Fallback TimeZone ----------------------------------------------
# BUG: Fix error variable not loading properly
# DEF_TZ & FALLBACK_TZ aren't loading properly on execution time
    # assignees: userS4B0
    # labels: priority_high, core, bug
    # milestone: v1.0.0

FALLBACK_TZ = "UTC"
