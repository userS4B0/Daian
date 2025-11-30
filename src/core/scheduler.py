from tabulate import tabulate
from datetime import datetime

from utils.time_utils import get_current_week, normalize_datetime

from config.app_settings import DEF_DATETIME_FMT, DEF_TABLE_FMT

from config.log.logger import setup_logger

logger = setup_logger(__name__)


class Scheduler:
    """
    Scheduler responsible for processing calendar events and identifying free time slots.
    This class assumes events are already normalized, sorted, and validated.
    """

    # ----- Main Constructor -----------------------------------------------
    def __init__(self):
        logger.debug("Scheduler initialized")

    # ----- Get free Google Calendar slots ---------------------------------
    @staticmethod
    def get_free_slots(
        events: list[dict],
        week_start: "datetime | None" = None,
        week_end: "datetime | None" = None,
    ) -> list[dict]:
        """
        Identify free time intervals in the weekly calendar.

        Args:
            events (list[dict]): List of calendar events already sorted by start time.
            week_start (datetime | None): Optional start of the week.
                If not provided, will use get_current_week() internally.
            week_end (datetime | None): Optional end of the week.
                If not provided, will use get_current_week() internally.

        Returns:
            list[dict]: List of free time slots as dictionaries with 'start' and 'end' keys.
        """
        logger.debug("Calculating free slots based on provided events")

        free_slots = []

        # Use provided week_start/week_end or fallback to get_current_week()
        if week_start is None or week_end is None:
            week_start_str, week_end_str = get_current_week()
            week_start = normalize_datetime(week_start_str)
            week_end = normalize_datetime(week_end_str)

        current = week_start  # Initial pointer at the start of the week

        for event in events:
            start_str = event.get("start", {}).get("dateTime") or event.get(
                "start", {}
            ).get("date")
            end_str = event.get("end", {}).get("dateTime") or event.get("end", {}).get(
                "date"
            )

            if not start_str or not end_str:
                logger.warning("Event without valid datetime fields detected")
                continue

            event_start = normalize_datetime(start_str)
            event_end = normalize_datetime(end_str)

            # If there is a gap between current pointer and next event, record it
            if event_start > current:
                free_slots.append({"start": current, "end": event_start})

            # Move pointer forward
            if event_end > current:
                current = event_end

        # Final gap until end of week
        if current < week_end:
            free_slots.append({"start": current, "end": week_end})

        logger.debug("Free slots calculated successfully")
        return free_slots

    # ----- Build free slots table -----------------------------------------
    @staticmethod
    def free_slots_totable(free_slots: list[dict]) -> str:
        """
        Convert a list of free slots into a formatted table string.

        Args:
            free_slots (List[Dict]): List of free slot dictionaries.

        Returns:
            str: A printable table generated with tabulate.
        """
        logger.debug("Converting free slots into a table")

        free_slot_table = []
        for slot in free_slots:
            free_slot_table.append(
                [
                    slot["start"].strftime(DEF_DATETIME_FMT),
                    slot["end"].strftime(DEF_DATETIME_FMT),
                    str(slot["end"] - slot["start"]),
                ]
            )

        headers = ["Free From", "Free Until", "Duration"]
        return tabulate(free_slot_table, headers=headers, tablefmt=DEF_TABLE_FMT)
