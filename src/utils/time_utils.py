from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config.user_settings import DEF_TZ, FALLBACK_TZ

# ----------------------------------------------------------------------
# Format Date Time
# ----------------------------------------------------------------------
def normalize_datetime(dt_str):
    """Convert an ISO 8601 datetime string to a UTC datetime object.

    Handles strings ending with 'Z' or offset-aware ISO formats.
    Falls back to UTC if the timezone cannot be determined.

    Args:
        dt_str (str): ISO 8601 formatted datetime string.

    Returns:
        datetime or None: Datetime object in UTC timezone, or None if input is invalid.
    """
    if not dt_str:
        return None

    try:
        # Convert 'Z' to '+00:00' for fromisoformat compatibility
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        # Invalid format
        return None

    try:
        return dt.astimezone(ZoneInfo(DEF_TZ))
    except Exception:
        # Fallback for environments without full zoneinfo support
        try:
            return dt.astimezone(ZoneInfo(FALLBACK_TZ))
        except Exception:
            # If all fails, return naive datetime
            return dt

# ----------------------------------------------------------------------
# Get Current week
# ----------------------------------------------------------------------
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
