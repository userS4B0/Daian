from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config.log.logger import setup_logger
from config.config_loader import ConfigLoader

config = ConfigLoader.load_and_validate()

logger = setup_logger(__name__)

DEF_TZ = config.get("app", {}).get("timezone", {}).get("default", {})
FALLBACK_TZ = config.get("app", {}).get("timezone", {}).get("fallback", {})


# ----- Format Date Time -----------------------------------------------
def normalize_datetime(dt_str: str):
    """Convert an ISO 8601 datetime string to a UTC datetime object.

    Handles strings ending with 'Z' or offset-aware ISO formats.
    Falls back to UTC if the timezone cannot be determined.

    Args:
        dt_str (str): ISO 8601 formatted datetime string.

    Returns:
        datetime or None: Datetime object in UTC timezone, or None if input is invalid.
    """
    logger.debug("Formating datetime")
    if not dt_str:
        logger.debug("No datetime string found")
        return None

    try:
        # Convert 'Z' to '+00:00' for fromisoformat compatibility
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        # Invalid format
        logger.debug("Invalid datetime format")
        return None

    try:
        return dt.astimezone(ZoneInfo(DEF_TZ))
    except Exception:
        logger.warning("DEF_TZ variable not found on .env, falling back to FALLBACK_TZ")

        # Fallback for environments without full zoneinfo support
        try:
            return dt.astimezone(ZoneInfo(FALLBACK_TZ))
        except Exception:
            logger.warning(
                "FALLBACK_TZ variable not defined on config, falling back to native datetime"
            )

            # If all fails, return naive datetime
            logger.debug("All attempts to format datetime failed, returning to dt")
            return dt


# ----- Get Current week -----------------------------------------------
def get_current_week() -> tuple[str, str]:
    """
    Get the start and end datetime of the current week in ISO 8601 format.

    The week starts on Monday 00:00:00 and ends on Sunday 23:59:59.

    Returns:
        tuple[str, str]: Tuple containing (time_min_iso, time_max_iso)
    """

    # Current datetime in specified timezone
    now = datetime.now(ZoneInfo(DEF_TZ))

    # Calculate start of the week (Monday 00:00)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate end of the week (Sunday 23:59:59)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    # Return ISO 8601 strings
    return start_of_week.isoformat(), end_of_week.isoformat()


# ----- Get Today ------------------------------------------------------
def get_today():
    """
    Return the current datetime based on the configured timezone.

    Returns:
        datetime: The current datetime in the most appropriate timezone available based on configuration.
    """
    try:
        today = datetime.now(DEF_TZ)

    except Exception:
        logger.warning("DEF_TZ variable not found on .env, falling back to FALLBACK_TZ")

        try:
            today = datetime.now(FALLBACK_TZ)

        except Exception:
            logger.warning(
                "FALLBACK_TZ variable not found on .env, falling back to native datetime"
            )
            logger.debug("All attempts to format datetime failed, returning to dt")

            today = datetime.now()
    return today


# ----- Is date expired ------------------------------------------------
def is_expired_by_days(due_date_str: str, days: int = 1) -> bool:
    """
    Check whether a date (ISO8601 string) expired more than `days` days ago.

    Args:
        due_date_str (str): Date string from Todoist (task.due.date).
        days (int): Number of days threshold.

    Returns:
        bool: True if the date is earlier than today - `days`.
    """
    if not due_date_str:
        return False

    # Normalize ISO date or return original value
    normalized = normalize_datetime(due_date_str)

    if not isinstance(normalized, datetime):
        # If normalization fails, the function returns the raw string
        # → this is not a valid datetime → skip gracefully
        return False

    due_date = normalized.date()
    today = get_today().date()

    return due_date < today - timedelta(days=days)
