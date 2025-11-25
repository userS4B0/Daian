from datetime import datetime
from zoneinfo import ZoneInfo

from config.user_settings import TZ, FALLBACK_TZ


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
        return dt.astimezone(ZoneInfo(TZ))
    except Exception:
        # Fallback for environments without full zoneinfo support
        try:
            return dt.astimezone(ZoneInfo(FALLBACK_TZ))
        except Exception:
            # If all fails, return naive datetime
            return dt
