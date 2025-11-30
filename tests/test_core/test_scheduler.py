# tests/test_core/test_scheduler.py
from datetime import datetime
from zoneinfo import ZoneInfo

from core.scheduler import Scheduler

# ----- Constants for tests ---------------------------------------------
TEST_TZ = "Europe/Madrid"
WEEK_START = datetime(2025, 12, 1, 0, 0, tzinfo=ZoneInfo(TEST_TZ))
WEEK_END = datetime(2025, 12, 7, 23, 59, 59, tzinfo=ZoneInfo(TEST_TZ))


# ----- get_free_slots Tests --------------------------------------------
def test_get_free_slots_no_events():
    """
    If there are no events, the free slot should be the entire week.
    """
    free_slots = Scheduler.get_free_slots([], week_start=WEEK_START, week_end=WEEK_END)
    assert free_slots == [{"start": WEEK_START, "end": WEEK_END}]


def test_get_free_slots_with_events():
    """
    Free slots should be calculated correctly around events.
    """
    events = [
        {
            "start": {"dateTime": "2025-12-01T10:00:00+01:00"},
            "end": {"dateTime": "2025-12-01T12:00:00+01:00"},
        },
        {
            "start": {"dateTime": "2025-12-02T14:00:00+01:00"},
            "end": {"dateTime": "2025-12-02T15:30:00+01:00"},
        },
    ]

    free_slots = Scheduler.get_free_slots(
        events, week_start=WEEK_START, week_end=WEEK_END
    )

    # Expected gaps:
    # 1. Week start → Event1 start
    # 2. Event1 end → Event2 start
    # 3. Event2 end → Week end
    assert free_slots[0]["start"] == WEEK_START
    assert free_slots[0]["end"].hour == 10

    assert free_slots[1]["start"].hour == 12
    assert free_slots[1]["end"].hour == 14

    assert free_slots[2]["start"].hour == 15
    assert free_slots[2]["end"] == WEEK_END


def test_get_free_slots_event_missing_datetime():
    """
    Events missing start or end datetime are skipped.
    """
    events = [
        {
            "start": {},  # Missing start
            "end": {"dateTime": "2025-12-01T12:00:00+01:00"},
        },
        {
            "start": {"dateTime": "2025-12-02T14:00:00+01:00"},
            "end": {"dateTime": "2025-12-02T15:30:00+01:00"},
        },
    ]

    free_slots = Scheduler.get_free_slots(
        events, week_start=WEEK_START, week_end=WEEK_END
    )

    # The first event is skipped, so free slot starts at week start → Event2 start
    assert free_slots[0]["start"] == WEEK_START
    assert free_slots[0]["end"].hour == 14

    # Remaining slot until week end
    assert free_slots[1]["start"].hour == 15
    assert free_slots[1]["end"] == WEEK_END
