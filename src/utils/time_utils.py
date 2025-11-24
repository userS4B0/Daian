from datetime import datetime
from zoneinfo import ZoneInfo

def normalize_datetime(dt_str):
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        try:
            return dt.astimezone(ZoneInfo("UTC"))
        except:
            return dt.astimezone(ZoneInfo("Etc/UTC"))
    except:
        return dt_str