"""
Unit tests for utils.time_utils module.

Covers:
- normalize_datetime(): conversion, fallback, and edge cases.
- get_current_week(): correct week boundaries and ISO formatting.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch

from utils.time_utils import normalize_datetime, get_current_week
from config.user_settings import DEF_TZ, FALLBACK_TZ


# ----- Tests normalize_datetime ---------------------------------------
def test_normalize_datetime_valid_utc_z():
    """
    Test normalize_datetime with ISO string ending in 'Z'.
    Should return datetime in DEF_TZ timezone.
    """
    dt_str = "2025-11-30T12:34:56Z"
    dt = normalize_datetime(dt_str)

    assert isinstance(dt, datetime)

    # Must be on DEF_TZ
    assert dt.tzinfo.key == DEF_TZ


def test_normalize_datetime_valid_offset():
    """
    Test normalize_datetime with ISO string containing an offset.
    Should return datetime in DEF_TZ timezone.
    """
    dt_str = "2025-11-30T12:34:56+02:00"
    dt = normalize_datetime(dt_str)

    assert isinstance(dt, datetime)
    assert dt.tzinfo.key == DEF_TZ


def test_normalize_datetime_empty_string():
    """
    Test normalize_datetime with empty string.
    Should return None.
    """
    assert normalize_datetime("") is None


def test_normalize_datetime_invalid_string():
    """
    Test normalize_datetime with invalid string.
    Should return None.
    """
    assert normalize_datetime("not a datetime") is None


def test_normalize_datetime_def_tz_missing(monkeypatch):
    """
    Test normalize_datetime when `DEF_TZ` is missing.
    Should fallback to `FALLBACK_TZ`.
    """
    dt_str = "2025-11-30T12:34:56+00:00"

    # Patch ZoneInfo to fail on `DEF_TZ`
    with patch(
        "utils.time_utils.ZoneInfo",
        side_effect=lambda tz: (_ for _ in ()).throw(KeyError("missing"))
        if tz == DEF_TZ
        else ZoneInfo(tz),
    ):
        dt = normalize_datetime(dt_str)
        assert isinstance(dt, datetime)
        assert dt.tzinfo.key == FALLBACK_TZ


def test_normalize_datetime_all_zones_missing(monkeypatch):
    """
    Test normalize_datetime when both DEF_TZ and FALLBACK_TZ fail.
    Should return naive datetime (tzinfo=None).
    """

    # Use naive ISO string to ensure tzinfo=None
    dt_str = "2025-11-30T12:34:56"

    # Patch ZoneInfo to fail on any zone
    with patch(
        "utils.time_utils.ZoneInfo",
        side_effect=lambda tz: (_ for _ in ()).throw(KeyError("missing")),
    ):
        dt = normalize_datetime(dt_str)
        assert isinstance(dt, datetime)
        assert dt.tzinfo is None  # naive


# ----- Tests get_current_week -----------------------------------------
def test_get_current_week_format():
    """
    Test get_current_week returns ISO 8601 strings for start and end of week.
    Start should be Monday 00:00:00, end should be Sunday 23:59:59.
    """
    start_iso, end_iso = get_current_week()

    # Check return types
    assert isinstance(start_iso, str)
    assert isinstance(end_iso, str)

    # Convert to datetime objects
    start_dt = datetime.fromisoformat(start_iso)
    end_dt = datetime.fromisoformat(end_iso)

    # Validate start of week
    assert start_dt.weekday() == 0
    assert start_dt.hour == 0 and start_dt.minute == 0 and start_dt.second == 0

    # Validate end of week
    assert end_dt.weekday() == 6
    assert end_dt.hour == 23 and end_dt.minute == 59 and end_dt.second == 59


def test_get_current_week_consistency(monkeypatch):
    """
    Test get_current_week with a fixed 'now' datetime.
    Ensures correct calculation of start (Monday) and end (Sunday) of week.
    """
    fixed_now = datetime(2025, 12, 3, 15, 20, 30, tzinfo=ZoneInfo(DEF_TZ))  # Wednesday

    # Patch datetime.now to return fixed date
    with patch("utils.time_utils.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_now
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        start_iso, end_iso = get_current_week()
        start_dt = datetime.fromisoformat(start_iso)
        end_dt = datetime.fromisoformat(end_iso)

        # Check start is Monday 00:00:00
        assert start_dt.weekday() == 0
        assert start_dt.hour == 0 and start_dt.minute == 0 and start_dt.second == 0

        # Check end is Sunday 23:59:59
        assert end_dt.weekday() == 6
        assert end_dt.hour == 23 and end_dt.minute == 59 and end_dt.second == 59

        # Validate duration of week
        delta_seconds = (end_dt - start_dt).total_seconds()
        expected_seconds = 6 * 24 * 3600 + 23 * 3600 + 59 * 60 + 59
        assert delta_seconds == expected_seconds
