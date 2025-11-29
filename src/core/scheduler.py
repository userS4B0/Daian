from datetime import datetime
from typing import List, Dict
from tabulate import tabulate
from config.log.logger import setup_logger

from utils.time_utils import get_current_week

logger = setup_logger(__name__)


class Scheduler:
    """
    Scheduler responsible for processing calendar events and identifying free time slots.
    This class assumes events are already normalized, sorted, and validated.
    """

    def __init__(self):
        logger.debug("Scheduler initialized")

    @staticmethod
    def get_free_slots(events: List[Dict]) -> List[Dict]:
        """
        Identify free time intervals in the weekly calendar.

        Args:
            events (List[Dict]): List of calendar events already sorted by start time.
            week_start (datetime): Start datetime of the week.
            week_end (datetime): End datetime of the week.

        Returns:
            List[Dict]: List of free time slots as dictionaries with start and end keys.
        """
        logger.debug("Calculating free slots based on provided events")

        free_slots = []

        # get_current_week returns ISO strings → convert to datetime
        week_start_str, week_end_str = get_current_week()

        week_start = datetime.fromisoformat(week_start_str)
        week_end = datetime.fromisoformat(week_end_str)

        # Initial pointer at the start of the week
        current = week_start

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

            event_start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            event_end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))

            # If there is a gap between current pointer and next event
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

    @staticmethod
    def free_slots_totable(free_slots: List[Dict]) -> str:
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
                    slot["start"].strftime("%Y-%m-%d %H:%M"),
                    slot["end"].strftime("%Y-%m-%d %H:%M"),
                    str(slot["end"] - slot["start"]),
                ]
            )

        headers = ["Free From", "Free Until", "Duration"]
        return tabulate(free_slot_table, headers=headers, tablefmt="grid")
